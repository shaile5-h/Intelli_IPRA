from datetime import datetime
from typing import List
from models.schemas import ExtractedInvoiceData, ValidationStatus

class ValidationService:
    def validate(self, data: ExtractedInvoiceData) -> ValidationStatus:
        errors = []
        
        # 1. Critical fields non-null (Pydantic handles some, but we check values)
        if not data.vendor_name: errors.append("vendor_name is missing")
        if not data.invoice_number: errors.append("invoice_number is missing")
        
        # 2. Confirm invoice_date conforms to ISO format (YYYY-MM-DD)
        try:
            datetime.strptime(data.invoice_date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"invoice_date '{data.invoice_date}' is not in ISO format (YYYY-MM-DD)")

        # 3. Ensure numeric amounts are greater than 0
        if data.total_amount <= 0:
            errors.append(f"total_amount {data.total_amount} must be greater than 0")
        
        for item in data.line_items:
            if item.qty <= 0:
                errors.append(f"Line item '{item.description}' qty must be > 0")
            if item.unit_price <= 0:
                errors.append(f"Line item '{item.description}' unit_price must be > 0")

        # 4. Verify currency is a valid 3-letter ISO code
        if not (data.currency and len(data.currency) == 3 and data.currency.isalpha()):
            errors.append(f"currency '{data.currency}' is not a valid 3-letter ISO code")

        return ValidationStatus(is_valid=len(errors) == 0, errors=errors)

validation_service = ValidationService()
