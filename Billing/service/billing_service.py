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
        self.booking_service_url = os.getenv(
            "BOOKING_SERVICE_URL", "http://booking_api:8003"
        )

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
        )
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
        valid = verify_response(query_params, self.vnp_hash_secret)
        if not valid:
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
        return {"status": "success" if success else "failed", "invoice_id": invoice_id}

    def handle_ipn(self, query_params: Dict[str, str]) -> dict:
        valid = verify_response(query_params, self.vnp_hash_secret)
        if not valid:
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
        return {"RspCode": "00", "Message": "Confirm Success"}

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
