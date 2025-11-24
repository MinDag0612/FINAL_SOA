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
from Billing.utils.vnpay import build_payment_url, verify_response
from Billing.utils.sepay import build_checkout_payload, create_checkout


class BillingService:
    """Billing service với VNPay (sandbox) và lưu DB."""

    def __init__(self, db_session: Session):
        self.repo = InvoiceRepository(db_session)
        self.vnp_tmn_code = os.getenv("VNP_TMNCODE", "DEMO1234")
        self.vnp_hash_secret = os.getenv(
            "VNP_HASHSECRET", "0123456789ABCDEF0123456789ABCDEF"
        )
        self.vnp_url = os.getenv(
            "VNP_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
        )
        self.vnp_return_url = os.getenv(
            "VNP_RETURNURL", "http://localhost:8002/billing/vnpay/return"
        )
        self.vnp_ipn_url = os.getenv(
            "VNP_IPNURL", "http://localhost:8002/billing/vnpay/ipn"
        )
        self.vnp_expire_minutes = int(os.getenv("VNP_EXPIRE_MINUTES", "15"))
        self.vnp_order_type = os.getenv("VNP_ORDER_TYPE", "other")
        self.vnp_time_offset_seconds = int(os.getenv("VNP_TIME_OFFSET_SECONDS", "0"))
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
        self.sepay_payment_method = os.getenv("SEPAY_PAYMENT_METHOD")

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

        if payload.method.lower() == "sepay":
            if not self.sepay_merchant_id or not self.sepay_secret_key:
                raise HTTPException(status_code=500, detail="SePay config missing")
            print(
                "[SEPAY][INIT]",
                {
                    "invoice_id": invoice_id,
                    "amount": invoice.amount,
                    "booking_id": payload.booking_id,
                    "success_url": self.sepay_success_url,
                    "error_url": self.sepay_error_url,
                    "cancel_url": self.sepay_cancel_url,
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
                success_url=self.sepay_success_url,
                error_url=self.sepay_error_url,
                cancel_url=self.sepay_cancel_url,
            )
            print("[SEPAY][INIT][PAYLOAD]", checkout_payload)
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
        print(
            "[VNPAY][INIT]",
            {
                "invoice_id": invoice_id,
                "amount": invoice.amount,
                "booking_id": payload.booking_id,
                "return_url": payload.return_url or self.vnp_return_url,
                "ipn_url": self.vnp_ipn_url,
                "time_offset": self.vnp_time_offset_seconds,
            },
        )
        url, params = build_payment_url(
            base_url=self.vnp_url,
            tmn_code=self.vnp_tmn_code,
            hash_secret=self.vnp_hash_secret,
            amount=invoice.amount,
            txn_ref=str(invoice_id),
            order_info=order_info,
            ip_addr=ip_addr,
            return_url=payload.return_url or self.vnp_return_url,
            expire_minutes=self.vnp_expire_minutes,
            order_type=self.vnp_order_type,
            ipn_url=self.vnp_ipn_url,
            time_offset_seconds=self.vnp_time_offset_seconds,
        )
        print("[VNPAY][INIT][PARAMS]", params)
        self.repo.update_payment_url(
            invoice_id,
            payment_url=url,
            payment_method=payload.method,
            vnp_txn_ref=str(invoice_id),
        )
        return {
            "invoice_id": invoice_id,
            "payment_method": payload.method,
            "payment_url": url,
            "vnp_params": params,
        }

    def handle_return(self, query_params: Dict[str, str]) -> dict:
        print("[VNPAY][RETURN][RAW]", query_params)
        valid = verify_response(query_params, self.vnp_hash_secret)
        if not valid:
            print("[VNPAY][RETURN][INVALID_SIGNATURE]")
            raise HTTPException(status_code=400, detail="Invalid signature")
        success = query_params.get("vnp_ResponseCode") == "00"
        invoice_id = int(query_params.get("vnp_TxnRef", "0"))
        booking_id = self._extract_booking_id(query_params.get("vnp_OrderInfo", ""))
        if success and booking_id:
            self.repo.update_status(
                invoice_id,
                status="paid",
                payment_reference=str(invoice_id),
                vnp_response_code=query_params.get("vnp_ResponseCode"),
                vnp_transaction_no=query_params.get("vnp_TransactionNo"),
            )
            self._notify_booking(booking_id, status="paid", reference_id=str(invoice_id))
        elif booking_id:
            self.repo.update_status(
                invoice_id,
                status="failed",
                payment_reference=str(invoice_id),
                vnp_response_code=query_params.get("vnp_ResponseCode"),
                vnp_transaction_no=query_params.get("vnp_TransactionNo"),
            )
            self._notify_booking(booking_id, status="failed", reference_id=str(invoice_id))
        print(
            "[VNPAY][RETURN][RESULT]",
            {"invoice_id": invoice_id, "booking_id": booking_id, "success": success},
        )
        return {"status": "success" if success else "failed", "invoice_id": invoice_id}

    def handle_ipn(self, query_params: Dict[str, str]) -> dict:
        print("[VNPAY][IPN][RAW]", query_params)
        valid = verify_response(query_params, self.vnp_hash_secret)
        if not valid:
            print("[VNPAY][IPN][INVALID_SIGNATURE]")
            return {"RspCode": "97", "Message": "Invalid signature"}
        response_code = query_params.get("vnp_ResponseCode")
        invoice_id = int(query_params.get("vnp_TxnRef", "0"))
        booking_id = self._extract_booking_id(query_params.get("vnp_OrderInfo", ""))
        success = response_code == "00"
        if booking_id:
            self.repo.update_status(
                invoice_id,
                status="paid" if success else "failed",
                payment_reference=str(invoice_id),
                vnp_response_code=response_code,
                vnp_transaction_no=query_params.get("vnp_TransactionNo"),
            )
            self._notify_booking(
                booking_id,
                status="paid" if success else "failed",
                reference_id=str(invoice_id),
            )
        print(
            "[VNPAY][IPN][RESULT]",
            {"invoice_id": invoice_id, "booking_id": booking_id, "success": success},
        )
        return {"RspCode": "00", "Message": "Confirm Success"}

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
