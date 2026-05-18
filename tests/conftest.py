import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_extracted_data():
    return {
        "vendor_name": "TechSupply Co.",
        "invoice_number": "INV-2024-001",
        "invoice_date": "2026-01-20",
        "line_items": [
            {"description": "Laptops", "qty": 5, "unit_price": 2500.0}
        ],
        "total_amount": 12500.0,
        "currency": "USD",
        "po_reference": "PO-1001"
    }
