import logging
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
    SePayCreatePaymentRequest,
)
from Billing.repository.invoice_repository import InvoiceRepository
from Billing.service.sepay_service import SePayService


class BillingService:
    """Billing service with SePay payment gateway integration."""

    def __init__(self, db_session: Session):
        self.repo = InvoiceRepository(db_session)
        self.booking_service_url = os.getenv(
            "BOOKING_SERVICE_URL", "http://booking_api:8003"
        )
        self.sepay_service = SePayService()
        self.logger = logging.getLogger(__name__)

    def create_invoice(self, payload: InvoiceCreate) -> Invoice:
        return self.repo.create(payload, status="pending")

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.repo.get(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice

    def initiate_payment(self, invoice_id: int, payload: PaymentRequest) -> dict:
        """Legacy payment initiation (marks as paid immediately)"""
        if payload.booking_id is None:
            raise HTTPException(status_code=400, detail="Missing booking_id for payment")
        
        # Mark as paid immediately (legacy flow)
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
            "message": "Invoice marked as paid",
        }

    def create_sepay_payment(self, invoice_id: int, payload: SePayCreatePaymentRequest) -> dict:
        """
        Create SePay payment link
        
        Args:
            invoice_id: Billing invoice ID
            payload: Payment creation request
        
        Returns:
            {
                "payment_url": "https://...",  # URL to redirect to SePay (or None if disabled)
                "booking_id": int,
                "amount": float,
                "merchant_id": str,
                "status": "pending" | "paid",
                "message": str
            }
        """
        # Verify invoice exists
        invoice = self.get_invoice(invoice_id)
        self.logger.info(
            "Creating SePay payment for invoice %s (booking %s)", invoice_id, payload.booking_id
        )
        
        if invoice.booking_id != payload.booking_id:
            raise HTTPException(
                status_code=400,
                detail="Invoice does not belong to the provided booking_id",
            )

        order_code = payload.order_code or f"invoice-{invoice_id}-booking-{payload.booking_id}"

        # Create SePay payment
        result = self.sepay_service.create_payment(
            booking_id=payload.booking_id,
            amount=payload.amount,
            description=payload.description,
            order_code=order_code,
        )
        result["invoice_id"] = invoice_id
        
        # If SePay is disabled, mark invoice as paid immediately
        if not self.sepay_service.enable_sepay:
            self.repo.update_status(
                invoice_id,
                status="paid",
                payment_reference=f"invoice-{invoice_id}",
            )
            self._notify_booking(
                payload.booking_id,
                status="paid",
                reference_id=str(invoice_id),
            )
        else:
            # Persist checkout info for traceability
            payment_url = result.get("payment_url")
            if payment_url:
                self.repo.update_payment_url(
                    invoice_id,
                    payment_url=payment_url,
                    payment_method="sepay",
                    vnp_txn_ref=order_code,
                )
        
        return result

    def handle_sepay_return(self, query_params: Dict[str, str]) -> dict:
        """
        Handle SePay return URL (user redirected here after payment)
        
        Args:
            query_params: Query parameters from SePay return URL
        
        Returns:
            {
                "success": bool,
                "booking_id": int,
                "status": str,
                "message": str,
                "redirect_url": str  # URL to redirect user to
            }
        """
        result = self.sepay_service.process_return(query_params)
        self.logger.info("SePay return payload processed: %s", result)
        
        booking_id = result.get("booking_id")
        invoice_id = result.get("invoice_id")
        order_code = result.get("order_code")
        transaction_id = result.get("transaction_id") or order_code or "unknown"
        status = result.get("status")
        message = result.get("message")
        gateway_payload = {
            "source": "sepay_return",
            "order_code": order_code,
            "transaction_id": transaction_id,
            "status": status,
        }

        if not result.get("success"):
            invoice_status = "cancelled" if status == "cancel" else "failed"
            if invoice_id:
                self.repo.update_status(
                    invoice_id,
                    status=invoice_status,
                    payment_reference=transaction_id,
                )
            if booking_id:
                self._notify_booking(
                    booking_id,
                    status="failed",
                    reference_id=transaction_id,
                    gateway_payload=gateway_payload,
                )

            reason = status or "failed"
            redirect_booking = f"&booking_id={booking_id}" if booking_id else ""
            return {
                "success": False,
                "booking_id": booking_id,
                "invoice_id": invoice_id,
                "status": status,
                "message": message,
                "redirect_url": f"/customer.html?payment=failed&reason={reason}{redirect_booking}",
            }

        # Payment successful
        if invoice_id:
            self.repo.update_status(
                invoice_id,
                status="paid",
                payment_reference=transaction_id,
            )

        if booking_id:
            self._notify_booking(
                booking_id,
                status="paid",
                reference_id=transaction_id,
                gateway_payload=gateway_payload,
            )

        redirect_booking = f"&booking_id={booking_id}" if booking_id else ""
        return {
            "success": True,
            "booking_id": booking_id,
            "invoice_id": invoice_id,
            "transaction_id": transaction_id,
            "status": "success",
            "message": message or "Payment successful",
            "redirect_url": f"/customer.html?payment=success{redirect_booking}",
        }

    def handle_sepay_ipn(self, payload: Dict) -> dict:
        """
        Handle SePay IPN webhook (server-to-server payment notification)
        
        Args:
            payload: IPN payload from SePay
        
        Returns:
            {"ok": true/false}  # SePay expects this format
        """
        result = self.sepay_service.process_ipn(payload)
        self.logger.info("SePay IPN received: %s", result)

        if "status" not in result:
            # Signature or payload invalid
            return {"ok": False, "message": result.get("message")}

        booking_id = result.get("booking_id")
        invoice_id = result.get("invoice_id")
        transaction_id = result.get("transaction_id") or result.get("order_code") or "unknown"
        status = result.get("status")
        gateway_payload = {
            "source": "sepay_ipn",
            "status": status,
            "order_code": result.get("order_code"),
            "transaction_id": transaction_id,
        }

        if invoice_id and status:
            target_status = "paid" if status == "paid" else "failed" if status == "failed" else status
            self.repo.update_status(
                invoice_id,
                status=target_status,
                payment_reference=transaction_id,
            )

        if booking_id and status in {"paid", "failed"}:
            self._notify_booking(
                booking_id,
                status=status,
                reference_id=transaction_id,
                gateway_payload=gateway_payload,
            )

        return {
            "ok": True,
            "message": result.get("message") or "IPN processed",
        }

    def handle_return(self, query_params: Dict[str, str]) -> dict:
        """Deprecated: use handle_sepay_return instead"""
        raise HTTPException(status_code=400, detail="Use /billing/sepay/return instead")

    def list_history(self, params: BillingHistoryParams) -> List[Invoice]:
        return self.repo.list_by_user(params.user_id, params.limit)

    def handle_webhook(self, invoice_id: int, payload: PaymentWebhook) -> dict:
        event = payload.event.lower()
        invoice = self.repo.get(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        if event == "cancel":
            self.repo.update_status(invoice_id, status="cancelled", payment_reference=str(invoice_id))
            # Notify booking
            booking_id = getattr(invoice, "booking_id", None)
            if booking_id:
                self._notify_booking(booking_id, status="failed", reference_id=str(invoice_id))
            return {"status": "cancelled", "invoice_id": invoice_id}

        raise HTTPException(status_code=400, detail=f"Unsupported webhook event: {event}")

    def _notify_booking(
        self,
        booking_id: Optional[int],
        status: str,
        reference_id: str,
        gateway_payload: Optional[dict] = None,
    ) -> None:
        """Notify booking service of payment status update"""
        if not booking_id:
            return
        try:
            payload = {
                "status": "paid" if status == "paid" else "failed",
                "reference_id": reference_id,
            }
            if gateway_payload:
                payload["gateway_payload"] = gateway_payload
            with httpx.Client(timeout=5.0) as client:
                client.post(
                    f"{self.booking_service_url}/booking/{booking_id}/payment-status",
                    json=payload,
                )
        except Exception:
            # Don't block IPN/return if notify fails
            pass

