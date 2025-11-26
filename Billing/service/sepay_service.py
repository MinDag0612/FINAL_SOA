"""
SePay Payment Gateway Integration Service
Handles payment creation, signature verification, and webhook processing
"""

import os
import hmac
import hashlib
import base64
import logging
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode


class SePayService:
    """SePay payment gateway service with HMAC-SHA256 signature verification"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.merchant_id = os.getenv("SEPAY_MERCHANT_ID", "")
        self.secret_key = os.getenv("SEPAY_SECRET_KEY", "")
        self.api_url = os.getenv("SEPAY_API_URL", "https://api.sandbox.sepay.vn")
        self.checkout_url = os.getenv("SEPAY_CHECKOUT_URL", "https://pay-sandbox.sepay.vn/v1/checkout/init")
        self.backend_public_url = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8002")
        self.return_endpoint = f"{self.backend_public_url}/billing/sepay/return"
        self.ipn_endpoint = f"{self.backend_public_url}/billing/sepay/ipn"
        self.api_version = os.getenv("SEPAY_API_VERSION", "3.0")
        requested_enable = os.getenv("ENABLE_SEPAY", "true").strip().lower()

        credentials_missing = not self.merchant_id or not self.secret_key
        if requested_enable == "false":
            self.enable_sepay = False
        elif credentials_missing:
            self.enable_sepay = False
            if requested_enable == "true":
                self.logger.warning(
                    "SEPAY credentials missing; running in mock mode (payments auto-approved)."
                )
            self.merchant_id = self.merchant_id or "demo-merchant"
            self.secret_key = self.secret_key or "demo-secret"
        else:
            self.enable_sepay = True

    def create_payment(
        self,
        booking_id: int,
        amount: float,
        description: str,
        order_code: str = None,
    ) -> Dict:
        """
        Create payment link for SePay checkout
        
        Args:
            booking_id: Booking ID for reference
            amount: Amount in VND
            description: Payment description
            order_code: Optional custom order code (defaults to booking_id)
        
        Returns:
            {
                "payment_url": "https://...",  # URL to redirect user to SePay
                "booking_id": booking_id,
                "amount": amount,
                "merchant_id": merchant_id,
                "checkout_url": checkout_url
            }
        """
        if not self.enable_sepay:
            # Mock payment when disabled
            return {
                "payment_url": None,
                "booking_id": booking_id,
                "amount": amount,
                "merchant_id": self.merchant_id,
                "checkout_url": None,
                "status": "paid",
                "message": "SePay disabled; marked as paid immediately",
            }

        order_code = order_code or f"booking-{booking_id}"
        ipn_url = self.ipn_endpoint
        base_return_url = f"{self.return_endpoint}?booking_id={booking_id}"
        cancel_url = f"{self.return_endpoint}?booking_id={booking_id}&status=cancel"

        # Build checkout payload
        payload = {
            "merchantId": self.merchant_id,
            "orderCode": order_code,
            "amount": int(amount),  # Amount in VND
            "description": description[:120],  # Truncate for gateway limit
            "cancelUrl": cancel_url,
            "returnUrl": base_return_url,
            "notificationUrl": ipn_url,
            "signature": "",  # Will be filled below
            "version": self.api_version,
        }

        # Create signature
        payload["signature"] = self._create_signature(payload)

        # Return URLs instead of making direct API call
        # Frontend will make the call to SePay
        query_string = urlencode(payload)
        payment_url = f"{self.checkout_url}?{query_string}"

        return {
            "payment_url": payment_url,
            "booking_id": booking_id,
            "amount": amount,
            "merchant_id": self.merchant_id,
            "order_code": order_code,
            "return_url": base_return_url,
            "status": "pending",
        }

    def _create_signature(self, payload: Dict) -> str:
        """
        Create HMAC-SHA256 signature for SePay request
        
        Algorithm:
        1. Sort keys alphabetically
        2. Join as key=value&key=value&...
        3. HMAC-SHA256 with secret_key
        4. Base64 encode
        """
        # Sort keys alphabetically (excluding signature field)
        sorted_keys = sorted(
            [
                k
                for k in payload.keys()
                if k != "signature" and payload.get(k) is not None and payload.get(k) != ""
            ]
        )
        
        # Build signature string
        signature_string = "&".join(
            [f"{k}={payload[k]}" for k in sorted_keys]
        )
        
        # Create HMAC-SHA256
        signature_bytes = hmac.new(
            self.secret_key.encode(),
            signature_string.encode(),
            hashlib.sha256,
        ).digest()
        
        # Base64 encode
        signature = base64.b64encode(signature_bytes).decode()
        
        return signature

    def verify_signature(self, payload: Dict) -> Tuple[bool, Optional[str]]:
        """
        Verify SePay IPN/Return signature
        
        Returns:
            (is_valid: bool, error_message: Optional[str])
        """
        if "signature" not in payload:
            return False, "Missing signature in payload"

        received_signature = payload.get("signature", "")
        
        # Create expected signature
        expected_signature = self._create_signature(payload)
        
        # Compare signatures (constant-time comparison to prevent timing attacks)
        is_valid = hmac.compare_digest(received_signature, expected_signature)
        
        if not is_valid:
            return False, f"Signature verification failed"
        
        return True, None

    def process_return(self, query_params: Dict[str, str]) -> Dict:
        """
        Process SePay return URL (user redirected here after payment)
        
        Returns:
            {
                "success": bool,
                "booking_id": int,
                "status": "success" | "cancel" | "failed",
                "transaction_id": str (if success),
                "message": str
            }
        """
        params = {k: v for k, v in query_params.items() if v not in (None, "")}
        status = (params.get("status") or params.get("code") or "failed").lower()
        booking_id = params.get("booking_id") or params.get("bookingId")
        order_code = params.get("orderCode") or params.get("order_code")
        transaction_id = params.get("transactionId") or params.get("transaction_id")
        amount = params.get("amount")
        invoice_id = self._extract_invoice_id(order_code) if order_code else None

        if self.enable_sepay and params:
            if "signature" in params:
                is_valid, error = self.verify_signature(params)
                if not is_valid:
                    return {
                        "success": False,
                        "booking_id": self._safe_int(booking_id),
                        "invoice_id": invoice_id,
                        "order_code": order_code,
                        "status": "failed",
                        "message": error or "Signature verification failed",
                    }
            else:
                self.logger.warning("SePay return payload missing signature")

        if not booking_id:
            return {
                "success": False,
                "status": "failed",
                "message": "Missing booking_id in return URL",
            }

        booking_id_int = self._safe_int(booking_id)
        if booking_id_int is None:
            return {
                "success": False,
                "status": "failed",
                "message": "Invalid booking_id format",
            }

        mapped_status = self._map_gateway_status(status)

        if mapped_status == "cancel":
            return {
                "success": False,
                "booking_id": booking_id_int,
                "invoice_id": invoice_id,
                "order_code": order_code,
                "status": "cancel",
                "message": "Payment cancelled by user",
            }

        if mapped_status == "success":
            return {
                "success": True,
                "booking_id": booking_id_int,
                "invoice_id": invoice_id,
                "order_code": order_code,
                "status": "success",
                "transaction_id": transaction_id or "unknown",
                "amount": amount,
                "message": "Payment successful",
            }

        return {
            "success": False,
            "booking_id": booking_id_int,
            "invoice_id": invoice_id,
            "order_code": order_code,
            "status": "failed",
            "message": f"Payment failed with status: {status}",
        }

    def process_ipn(self, payload: Dict) -> Dict:
        """
        Process SePay IPN webhook (server-to-server payment notification)
        
        Args:
            payload: IPN payload from SePay
        
        Returns:
            {
                "success": bool,
                "booking_id": int,
                "transaction_id": str,
                "status": "paid" | "failed" | "pending",
                "message": str
            }
        """
        # Verify signature
        is_valid, error_msg = self.verify_signature(payload)
        if not is_valid:
            return {
                "success": False,
                "message": f"IPN signature verification failed: {error_msg}",
            }

        # Extract IPN data
        order_code = payload.get("orderCode", "")
        transaction_id = payload.get("transactionId", "")
        ipn_status = payload.get("status", "")

        # Extract booking_id from order_code (format: booking-{id})
        booking_id = self._extract_booking_id(order_code)
        invoice_id = self._extract_invoice_id(order_code)
        if not booking_id:
            return {
                "success": False,
                "message": f"Could not extract booking_id from order_code: {order_code}",
            }

        # Map SePay status to our status
        payment_status = self._map_gateway_status(ipn_status)
        normalized_status = (
            "paid" if payment_status == "success" else "failed" if payment_status == "cancel" else payment_status
        )

        return {
            "success": normalized_status == "paid",
            "booking_id": booking_id,
            "invoice_id": invoice_id,
            "transaction_id": transaction_id,
            "order_code": order_code,
            "status": normalized_status,
            "raw_status": ipn_status,
            "message": f"Payment {normalized_status}",
        }

    def _extract_booking_id(self, order_code: str) -> Optional[int]:
        """Extract booking_id from order_code (e.g., 'booking-123' -> 123)"""
        if not order_code:
            return None
        cleaned = order_code.replace("_", "-")
        parts = [p for p in cleaned.split("-") if p]
        for idx, part in enumerate(parts):
            if part.lower() == "booking" and idx + 1 < len(parts):
                return self._safe_int(parts[idx + 1])
        # Fallback: last numeric token
        for token in reversed(parts):
            value = self._safe_int(token)
            if value is not None:
                return value
        return None

    def _extract_invoice_id(self, order_code: str) -> Optional[int]:
        """Extract invoice_id from order_code (e.g., 'invoice-456-booking-123' -> 456)"""
        if not order_code:
            return None
        cleaned = order_code.replace("_", "-")
        parts = [p for p in cleaned.split("-") if p]
        for idx, part in enumerate(parts):
            if part.lower() == "invoice" and idx + 1 < len(parts):
                return self._safe_int(parts[idx + 1])
        return None

    def _map_gateway_status(self, status: str) -> str:
        normalized = (status or "").lower()
        if normalized in {"success", "00"}:
            return "success"
        if normalized in {"cancel", "cancelled"}:
            return "cancel"
        if normalized in {"failed", "01", "02"}:
            return "failed"
        return normalized or "failed"

    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None
