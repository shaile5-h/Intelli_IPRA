from typing import Dict, List, Optional
from models.schemas import PurchaseOrder, ReconciliationReport

# Mock Purchase Order Data from requirements
MOCK_POS = [
    {
        "po_number": "PO-1001",
        "vendor_name": "TechSupply Co.",
        "po_date": "2026-01-15",
        "total_amount": 12500.00,
        "currency": "USD",
        "status": "OPEN"
    },
    {
        "po_number": "PO-1002",
        "vendor_name": "CloudParts Ltd.",
        "po_date": "2026-02-10",
        "total_amount": 8750.50,
        "currency": "USD",
        "status": "OPEN"
    },
    {
        "po_number": "PO-1003",
        "vendor_name": "DataEdge Pvt. Ltd.",
        "po_date": "2026-03-01",
        "total_amount": 3200.00,
        "currency": "USD",
        "status": "OPEN"
    },
    {
        "po_number": "PO-1004",
        "vendor_name": "NetworkPros Inc.",
        "po_date": "2026-03-20",
        "total_amount": 21000.00,
        "currency": "USD",
        "status": "CLOSED"
    }
]

class StorageService:
    def __init__(self):
        # In-memory storage for invoices and reports
        self.invoices: Dict[str, dict] = {}  # invoice_id -> raw_data
        self.reports: Dict[str, ReconciliationReport] = {}  # invoice_id -> report
        self.processed_invoice_numbers: set = set() # For duplicate detection
        
        # Initialize POs
        self.pos: Dict[str, PurchaseOrder] = {
            po["po_number"]: PurchaseOrder(**po) for po in MOCK_POS
        }

    def save_invoice(self, invoice_id: str, data: dict):
        self.invoices[invoice_id] = data

    def get_invoice(self, invoice_id: str) -> Optional[dict]:
        return self.invoices.get(invoice_id)

    def save_report(self, invoice_id: str, report: ReconciliationReport):
        self.reports[invoice_id] = report
        if report.extracted_data:
            self.processed_invoice_numbers.add(report.extracted_data.invoice_number)

    def get_report(self, invoice_id: str) -> Optional[ReconciliationReport]:
        return self.reports.get(invoice_id)

    def get_po(self, po_number: str) -> Optional[PurchaseOrder]:
        return self.pos.get(po_number)

    def is_duplicate_invoice(self, invoice_number: str) -> bool:
        return invoice_number in self.processed_invoice_numbers

# Singleton instance
storage_service = StorageService()
