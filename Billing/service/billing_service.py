import os
from typing import Dict, List, Optional
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from Billing.models.billing_models import (
    BillingHistoryParams,
    Invoice,
    InvoiceCreate,
    PaymentRequest,
    PaymentWebhook,
)
from Billing.repository.invoice_repository import InvoiceRepository
class BillingService:
    """Billing service (SePay disabled; marks invoices as paid immediately)."""

    def __init__(self, db_session: Session):
        self.repo = InvoiceRepository(db_session)
        self.booking_service_url = os.getenv(
            "BOOKING_SERVICE_URL", "http://booking_api:8003"
        )
        # SePay disabled; keep booking URL for callbacks only
        self.sepay_base_url = None
        self.sepay_checkout_url = None
        self.sepay_merchant_id = ""
        self.sepay_secret_key = ""
        self.sepay_success_url = None
        self.sepay_error_url = None
        self.sepay_cancel_url = None
        self.sepay_operation = None
        self.sepay_currency = "VND"
        self.sepay_payment_method = None

    def _build_callback_url(self, base_url: Optional[str], invoice_id: int, redirect_url: Optional[str]) -> Optional[str]:
        # Deprecated helper; left for compatibility
        return None

    def create_invoice(self, payload: InvoiceCreate) -> Invoice:
        return self.repo.create(payload, status="pending")

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.repo.get(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice

    def initiate_payment(self, invoice_id: int, payload: PaymentRequest) -> dict:
        if payload.booking_id is None:
            raise HTTPException(status_code=400, detail="Missing booking_id for payment")
        # Gateway disabled: mark as paid immediately to unblock flow.
        self.repo.update_status(
            invoice_id,
            status="paid",
            payment_reference=str(invoice_id),
        )
        self._notify_booking(payload.booking_id, status="paid", reference_id=str(invoice_id))
        return {
            "invoice_id": invoice_id,
            "payment_method": payload.method,
            "status": "paid",
            "message": "Payment gateway disabled; invoice marked as paid",
        }

    def handle_return(self, query_params: Dict[str, str]) -> dict:
        raise HTTPException(status_code=400, detail="VNPAY disabled")

    def handle_sepay_ipn(self, body: Dict) -> dict:
        raise HTTPException(status_code=400, detail="SePay gateway disabled")

    def handle_sepay_return(self, query_params: Dict[str, str]):
        raise HTTPException(status_code=400, detail="SePay gateway disabled")

    def list_history(self, params: BillingHistoryParams) -> List[Invoice]:
        return self.repo.list_by_user(params.user_id, params.limit)

    def handle_webhook(self, invoice_id: int, payload: PaymentWebhook) -> dict:
        event = payload.event.lower()
        invoice = self.repo.get(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        if event == "cancel":
            self.repo.update_status(invoice_id, status="cancelled", payment_reference=str(invoice_id))
            # đồng bộ về booking để cập nhật payment_status/booking status
            booking_id = getattr(invoice, "booking_id", None)
            if booking_id:
                self._notify_booking(booking_id, status="failed", reference_id=str(invoice_id))
            return {"status": "cancelled", "invoice_id": invoice_id}

        raise HTTPException(status_code=400, detail=f"Unsupported webhook event: {event}")

    def _extract_booking_id(self, order_info: str) -> Optional[int]:
        if "booking" in order_info.lower():
            tokens = order_info.replace("(", " ").replace(")", " ").replace("#", " ").split()
            for idx, tok in enumerate(tokens):
                if tok.lower() == "booking" and idx + 1 < len(tokens):
                    try:
                        return int(tokens[idx + 1])
                    except ValueError:
                        continue
        return None

    def _notify_booking(self, booking_id: int, status: str, reference_id: str) -> None:
        try:
            payload = {"status": "paid" if status == "paid" else "failed", "reference_id": reference_id}
            with httpx.Client(timeout=5.0) as client:
                client.post(
                    f"{self.booking_service_url}/booking/{booking_id}/payment-status",
                    json=payload,
                )
        except Exception:
            # không chặn IPN/return nếu notify thất bại
            pass
