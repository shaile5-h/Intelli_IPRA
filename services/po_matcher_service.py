from typing import Optional
from models.schemas import PurchaseOrder
from storage.memory_storage import storage_service

class POMatcherService:
    def match(self, po_reference: Optional[str]) -> Optional[PurchaseOrder]:
        if not po_reference:
            return None
        return storage_service.get_po(po_reference)

po_matcher_service = POMatcherService()
