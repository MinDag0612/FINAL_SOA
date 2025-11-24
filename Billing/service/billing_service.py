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
from Billing.utils.sepay import build_checkout_payload, create_checkout


class BillingService:
    """Billing service với SePay sandbox và lưu DB."""

    def __init__(self, db_session: Session):
        self.repo = InvoiceRepository(db_session)
        self.booking_service_url = os.getenv(
            "BOOKING_SERVICE_URL", "http://booking_api:8003"
        )
        # SePay
        self.sepay_base_url = os.getenv("SEPAY_BASE_URL", "https://pgapi-sandbox.sepay.vn")
        self.sepay_checkout_url = os.getenv(
            "SEPAY_CHECKOUT_URL", "https://pay-sandbox.sepay.vn/v1/checkout/init"
        )
        self.sepay_merchant_id = os.getenv("SEPAY_MERCHANT_ID", "")
        self.sepay_secret_key = os.getenv("SEPAY_SECRET_KEY", "")
        self.sepay_success_url = os.getenv("SEPAY_SUCCESS_URL")
        self.sepay_error_url = os.getenv("SEPAY_ERROR_URL")
        self.sepay_cancel_url = os.getenv("SEPAY_CANCEL_URL")
        self.sepay_operation = os.getenv("SEPAY_OPERATION", "PURCHASE")
        self.sepay_currency = os.getenv("SEPAY_CURRENCY", "VND")
        self.sepay_payment_method = os.getenv("SEPAY_PAYMENT_METHOD", "ATM")  # sandbox default

    def _url_with_invoice(self, url: Optional[str], invoice_id: int) -> Optional[str]:
        """Append invoice_id query param to return/error/cancel URL if provided."""
        if not url:
            return None
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}invoice_id={invoice_id}"

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
        invoice = self.get_invoice(invoice_id)
        order_info = f"Thanh toan don dat san #{invoice_id} (booking {payload.booking_id})"
        ip_addr = "127.0.0.1"
        success_url = self._url_with_invoice(self.sepay_success_url, invoice_id)
        error_url = self._url_with_invoice(self.sepay_error_url, invoice_id)
        cancel_url = self._url_with_invoice(self.sepay_cancel_url, invoice_id)

        if payload.method.lower() == "sepay":
            if not self.sepay_merchant_id or not self.sepay_secret_key:
                raise HTTPException(status_code=500, detail="SePay config missing")
            print(
                "[SEPAY][INIT]",
                {
                    "invoice_id": invoice_id,
                    "amount": invoice.amount,
                    "booking_id": payload.booking_id,
                    "success_url": success_url,
                    "error_url": error_url,
                    "cancel_url": cancel_url,
                },
            )
            checkout_payload, signature = build_checkout_payload(
                merchant_id=self.sepay_merchant_id,
                secret_key=self.sepay_secret_key,
                amount=invoice.amount,
                invoice_id=str(invoice_id),
                description=order_info,
                currency=self.sepay_currency,
                operation=self.sepay_operation,
                payment_method=self.sepay_payment_method,
                success_url=success_url,
                error_url=error_url,
                cancel_url=cancel_url,
                customer_id=str(invoice.user_id),
            )
            print("[SEPAY][INIT][PAYLOAD]", checkout_payload)
            # Probe SePay response for debugging (no redirect)
            try:
                probe = create_checkout(
                    checkout_url=self.sepay_checkout_url,
                    payload=checkout_payload,
                    timeout=10.0,
                    follow_redirects=False,
                )
                print("[SEPAY][PROBE]", probe)
            except Exception as exc:
                print("[SEPAY][PROBE][ERROR]", exc)
            # SePay yêu cầu POST form; trả về form/endpoint để frontend tự submit thay vì gọi server-to-server
            payment_url = self.sepay_checkout_url
            inputs = "".join(
                [f"<input type='hidden' name='{k}' value='{v}' />" for k, v in checkout_payload.items()]
            )
            form_html = (
                f"<form id='sepay_form' method='POST' action='{payment_url}'>"
                f"{inputs}</form><script>document.getElementById('sepay_form').submit();</script>"
            )
            self.repo.update_payment_url(
                invoice_id,
                payment_url=str(payment_url),
                payment_method=payload.method,
                vnp_txn_ref=str(invoice_id),
            )
            return {
                "invoice_id": invoice_id,
                "payment_method": payload.method,
                "payment_url": payment_url,
                "payload": checkout_payload,
                "signature": signature,
                "form_html": form_html,
            }
        raise HTTPException(status_code=400, detail="Unsupported payment method")

    def handle_return(self, query_params: Dict[str, str]) -> dict:
        raise HTTPException(status_code=400, detail="VNPAY disabled")

    # ---- SePay ----
    def handle_sepay_ipn(self, body: Dict) -> dict:
        print("[SEPAY][IPN][RAW]", body)
        invoice_ref = body.get("order_invoice_number") or body.get("invoice_id") or body.get("order_id")
        try:
            invoice_id = int(invoice_ref)
        except Exception:
            invoice_id = 0
        status_raw = str(body.get("status") or body.get("order_status") or "").lower()
        success = status_raw in ("success", "completed", "paid", "00", "0")
        booking_id = None
        if invoice_id:
            invoice = self.repo.get(invoice_id)
            booking_id = getattr(invoice, "booking_id", None) if invoice else None
            if invoice:
                self.repo.update_status(
                    invoice_id,
                    status="paid" if success else "failed",
                    payment_reference=str(invoice_id),
                    vnp_response_code=body.get("status"),
                    vnp_transaction_no=body.get("transaction_id") or body.get("trans_id"),
                )
                if booking_id:
                    self._notify_booking(
                        booking_id,
                        status="paid" if success else "failed",
                        reference_id=str(invoice_id),
                    )
        print(
            "[SEPAY][IPN][RESULT]",
            {"invoice_id": invoice_id, "booking_id": booking_id, "success": success, "status": status_raw},
        )
        return {"code": "00", "message": "received"}

    def handle_sepay_return(self, query_params: Dict[str, str]) -> dict:
        print("[SEPAY][RETURN][RAW]", query_params)
        invoice_ref = query_params.get("order_invoice_number") or query_params.get("invoice_id")
        try:
            invoice_id = int(invoice_ref) if invoice_ref else 0
        except Exception:
            invoice_id = 0
        status_raw = str(query_params.get("status") or query_params.get("order_status") or "").lower()
        success = status_raw in ("success", "completed", "paid", "00", "0")
        booking_id = None
        if invoice_id:
            invoice = self.repo.get(invoice_id)
            booking_id = getattr(invoice, "booking_id", None) if invoice else None
            if invoice:
                self.repo.update_status(
                    invoice_id,
                    status="paid" if success else "failed",
                    payment_reference=str(invoice_id),
                    vnp_response_code=query_params.get("status"),
                    vnp_transaction_no=query_params.get("transaction_id") or query_params.get("trans_id"),
                )
                if booking_id:
                    self._notify_booking(
                        booking_id,
                        status="paid" if success else "failed",
                        reference_id=str(invoice_id),
                    )
        return {"status": "success" if success else "failed", "invoice_id": invoice_id, "raw": query_params}

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
