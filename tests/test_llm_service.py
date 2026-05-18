import pytest
from unittest.mock import patch, MagicMock
from services.llm_service import LLMService
from models.schemas import ExtractedInvoiceData

@pytest.mark.asyncio
@patch("google.generativeai.GenerativeModel.generate_content")
async def test_extract_invoice_data_success(mock_generate):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.candidates = [MagicMock(finish_reason=1)]
    mock_response.text = """
    ```json
    {
      "vendor_name": "Test Vendor",
      "invoice_number": "INV-001",
      "invoice_date": "2023-01-01",
      "line_items": [{"description": "Item 1", "qty": 1, "unit_price": 10.0}],
      "total_amount": 10.0,
      "currency": "USD",
      "po_reference": "PO-123"
    }
    ```
    """
    mock_generate.return_value = mock_response

    service = LLMService()
    result = await service.extract_invoice_data("some content")

    assert result is not None
    assert result.vendor_name == "Test Vendor"
    assert result.invoice_number == "INV-001"
    assert result.total_amount == 10.0

@pytest.mark.asyncio
@patch("google.generativeai.GenerativeModel.generate_content")
async def test_extract_invoice_data_normalization(mock_generate):
    # Setup mock response with missing fields
    mock_response = MagicMock()
    mock_response.candidates = [MagicMock(finish_reason=1)]
    mock_response.text = '{"vendor_name": "Test"}' # Missing almost everything
    mock_generate.return_value = mock_response

    service = LLMService()
    result = await service.extract_invoice_data("some content")

    assert result is not None
    assert result.vendor_name == "Test"
    assert result.invoice_number == "N/A" # Normalized
    assert result.total_amount == 0.0 # Normalized
    assert result.line_items == [] # Normalized
