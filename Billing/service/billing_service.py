from typing import List
from models.billing_models import (
    BillingHistoryParams,
    Invoice,
    InvoiceCreate,
    PaymentRequest,
    PaymentWebhook,
)


class BillingService:
    """Stub billing service."""

    def __init__(self):
        self._invoice = Invoice(
            invoice_id=1,
            booking_id=1,
            user_id=9,
            amount=150000,
            currency="VND",
            status="draft",
        )

    def create_invoice(self, payload: InvoiceCreate) -> Invoice:
        return Invoice(
            invoice_id=77,
            booking_id=payload.booking_id,
            user_id=payload.user_id,
            amount=payload.amount,
            currency=payload.currency,
            status="pending",
        )

    def get_invoice(self, invoice_id: int) -> Invoice:
        return self._invoice.copy(update={"invoice_id": invoice_id})

    def initiate_payment(self, invoice_id: int, payload: PaymentRequest) -> dict:
        return {
            "invoice_id": invoice_id,
            "payment_method": payload.method,
            "redirect_url": payload.return_url or "https://sandbox-payments/redirect",
            "message": "Stub initiate payment – chưa gọi PSP",
        }

    def handle_webhook(self, invoice_id: int, payload: PaymentWebhook) -> dict:
        return {
            "invoice_id": invoice_id,
            "received_event": payload.event,
            "status": "processed",
            "message": "Stub webhook – chưa xác thực chữ ký",
        }

    def list_history(self, params: BillingHistoryParams) -> List[Invoice]:
        return [
            self._invoice.copy(
                update={"invoice_id": idx + 1, "status": "paid", "user_id": params.user_id}
            )
            for idx in range(min(params.limit, 3))
        ]
