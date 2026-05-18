import pytest
from unittest.mock import patch, MagicMock
from models.schemas import ExtractedInvoiceData, ReconciliationReport, ReconciliationStatus

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    # Root now returns index.html if it exists, otherwise a JSON message
    # Since we are testing in an environment where frontend/index.html exists, it might return HTML
    assert response.status_code == 200

def test_upload_json_payload(client):
    payload = '{"test": "data"}'
    response = client.post("/api/v1/upload", data={"payload": payload})
    assert response.status_code == 200
    data = response.json()
    assert "invoice_id" in data
    assert data["message"] == "Invoice uploaded successfully"

def test_upload_file(client):
    file_content = b"fake invoice content"
    files = {"file": ("invoice.pdf", file_content, "application/pdf")}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "invoice_id" in data
    assert data["message"] == "Invoice uploaded successfully"

@patch("services.llm_service.llm_service.extract_invoice_data")
def test_reconcile_invoice_success(mock_extract, client, mock_extracted_data):
    # Setup mock
    mock_extract.return_value = ExtractedInvoiceData(**mock_extracted_data)
    
    # 1. Upload
    upload_res = client.post("/api/v1/upload", data={"payload": '{"key": "val"}'})
    invoice_id = upload_res.json()["invoice_id"]
    
    # 2. Reconcile
    reconcile_res = client.post(f"/api/v1/reconcile/{invoice_id}")
    assert reconcile_res.status_code == 200
    report = reconcile_res.json()
    
    assert report["invoice_id"] == invoice_id
    assert report["reconciliation_status"] == "MATCHED"
    assert report["extracted_data"]["vendor_name"] == mock_extracted_data["vendor_name"]
    assert report["matched_po"]["po_number"] == "PO-1001"

@patch("services.llm_service.llm_service.extract_invoice_data")
def test_reconcile_invoice_partial_variance(mock_extract, client, mock_extracted_data):
    # Modify data to cause variance (PO-1001 is 12500.0)
    mock_extracted_data["total_amount"] = 14000.0 
    mock_extract.return_value = ExtractedInvoiceData(**mock_extracted_data)
    
    # 1. Upload
    upload_res = client.post("/api/v1/upload", data={"payload": '{"key": "val"}'})
    invoice_id = upload_res.json()["invoice_id"]
    
    # 2. Reconcile
    reconcile_res = client.post(f"/api/v1/reconcile/{invoice_id}")
    assert reconcile_res.status_code == 200
    report = reconcile_res.json()
    
    assert report["reconciliation_status"] == "PARTIAL"
    assert any(a["type"] == "AMOUNT_VARIANCE" for a in report["anomalies"])

def test_reconcile_non_existent_invoice(client):
    response = client.post("/api/v1/reconcile/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"

def test_get_report_not_found(client):
    response = client.get("/api/v1/report/non-existent-id")
    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]
