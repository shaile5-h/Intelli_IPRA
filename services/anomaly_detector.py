from typing import List, Optional
from models.schemas import ExtractedInvoiceData, PurchaseOrder, Anomaly
from storage.memory_storage import storage_service

class AnomalyDetector:
    def detect(self, data: ExtractedInvoiceData, po: Optional[PurchaseOrder]) -> List[Anomaly]:
        anomalies = []

        # (a) Amount variance > 5%
        if po:
            variance = abs(data.total_amount - po.total_amount)
            threshold = 0.05 * po.total_amount
            if variance > threshold:
                anomalies.append(Anomaly(
                    type="AMOUNT_VARIANCE",
                    message=f"Invoice amount {data.total_amount} varies from PO amount {po.total_amount} by more than 5%"
                ))

        # (b) Missing or unmatched PO reference
        if not data.po_reference:
            anomalies.append(Anomaly(
                type="MISSING_PO_REFERENCE",
                message="PO reference is missing from the invoice"
            ))
        elif not po:
            anomalies.append(Anomaly(
                type="UNMATCHED_PO_REFERENCE",
                message=f"PO reference '{data.po_reference}' not found in system"
            ))

        # (c) Duplicate invoice_number
        if storage_service.is_duplicate_invoice(data.invoice_number):
            anomalies.append(Anomaly(
                type="DUPLICATE_INVOICE",
                message=f"Invoice number '{data.invoice_number}' has already been processed"
            ))

        return anomalies

anomaly_detector = AnomalyDetector()
