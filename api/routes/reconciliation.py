from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from typing import Optional
import uuid
from models.schemas import (
    ReconciliationReport, 
    ReconciliationStatus, 
    ValidationStatus,
    ExtractedInvoiceData
)
from storage.memory_storage import storage_service
from services.llm_service import llm_service
from services.validation_service import validation_service
from services.po_matcher_service import po_matcher_service
from services.anomaly_detector import anomaly_detector

router = APIRouter()

@router.post("/upload")
async def upload_invoice(
    file: Optional[UploadFile] = File(None),
    payload: Optional[dict] = Body(None)
):
    """
    Ingest invoice via file upload or JSON payload.
    """
    invoice_id = str(uuid.uuid4())
    
    if file:
        content = await file.read()
        storage_service.save_invoice(invoice_id, {"content": content, "is_file": True, "filename": file.filename})
    elif payload:
        storage_service.save_invoice(invoice_id, {"content": payload, "is_file": False})
    else:
        raise HTTPException(status_code=400, detail="Either file or JSON payload must be provided")
    
    return {"invoice_id": invoice_id, "message": "Invoice uploaded successfully"}

@router.post("/reconcile/{invoice_id}", response_model=ReconciliationReport)
async def reconcile_invoice(invoice_id: str):
    """
    Trigger the reconciliation pipeline for a given invoice_id.
    """
    invoice_data = storage_service.get_invoice(invoice_id)
    if not invoice_data:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # 1. Extraction
    extracted_data = await llm_service.extract_invoice_data(
        invoice_data["content"], 
        is_file=invoice_data["is_file"]
    )
    
    if not extracted_data:
        # If extraction fails completely, return a failed report
        report = ReconciliationReport(
            invoice_id=invoice_id,
            validation_status=ValidationStatus(is_valid=False, errors=["LLM extraction failed"]),
            reconciliation_status=ReconciliationStatus.FAILED
        )
        storage_service.save_report(invoice_id, report)
        return report

    # 2. Validation
    validation_status = validation_service.validate(extracted_data)

    # 3. PO Matching
    matched_po = po_matcher_service.match(extracted_data.po_reference)

    # 4. Anomaly Detection
    anomalies = anomaly_detector.detect(extracted_data, matched_po)

    # 5. Determine Reconciliation Status
    if not validation_status.is_valid:
        status = ReconciliationStatus.FAILED
    elif anomalies:
        status = ReconciliationStatus.PARTIAL
    else:
        status = ReconciliationStatus.MATCHED

    report = ReconciliationReport(
        invoice_id=invoice_id,
        extracted_data=extracted_data,
        validation_status=validation_status,
        matched_po=matched_po,
        anomalies=anomalies,
        reconciliation_status=status
    )

    storage_service.save_report(invoice_id, report)
    return report

@router.get("/report/{invoice_id}", response_model=ReconciliationReport)
async def get_report(invoice_id: str):
    """
    Fetch the complete reconciliation report for a given invoice_id.
    """
    report = storage_service.get_report(invoice_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found. Please trigger reconciliation first.")
    return report
