from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ReconciliationStatus(str, Enum):
    MATCHED = "MATCHED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

class LineItem(BaseModel):
    description: str
    qty: float
    unit_price: float

class ExtractedInvoiceData(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_date: str  # Will validate ISO format in service
    line_items: List[LineItem]
    total_amount: float
    currency: str
    po_reference: Optional[str] = None

class ValidationStatus(BaseModel):
    is_valid: bool
    errors: List[str] = []

class Anomaly(BaseModel):
    type: str
    message: str

class PurchaseOrder(BaseModel):
    po_number: str
    vendor_name: str
    po_date: str
    total_amount: float
    currency: str
    status: str

class ReconciliationReport(BaseModel):
    invoice_id: str
    extracted_data: Optional[ExtractedInvoiceData] = None
    validation_status: ValidationStatus
    matched_po: Optional[PurchaseOrder] = None
    anomalies: List[Anomaly] = []
    reconciliation_status: ReconciliationStatus
