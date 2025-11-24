import base64
import hashlib
import hmac
from typing import Dict, Tuple

import httpx


def sign_checkout(data: Dict[str, str], secret_key: str) -> str:
    """
    Ký theo đúng thứ tự formFields của SDK PHP (merchant, currency, order_amount, operation, order_description,
    payment_method, order_invoice_number, customer_id, success_url, error_url, cancel_url, ...). Ghép key=value bằng
    dấu phẩy theo thứ tự xuất hiện trong payload.
    """
    allowed = {
        "merchant",
        "env",
        "operation",
        "payment_method",
        "order_amount",
        "currency",
        "order_invoice_number",
        "order_description",
        "customer_id",
        "agreement_id",
        "agreement_name",
        "agreement_type",
        "agreement_payment_frequency",
        "agreement_amount_per_payment",
        "success_url",
        "error_url",
        "cancel_url",
    }
    sign_parts = []
    for field in data.keys():
        if field in allowed:
            sign_parts.append(f"{field}={data.get(field) or ''}")
    sign_data = ",".join(sign_parts)
    digest = hmac.new(secret_key.encode(), sign_data.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def build_checkout_payload(
    merchant_id: str,
    secret_key: str,
    amount: float,
    invoice_id: str,
    description: str,
    currency: str = "VND",
    operation: str = "PURCHASE",
    payment_method: str | None = None,
    success_url: str | None = None,
    error_url: str | None = None,
    cancel_url: str | None = None,
    customer_id: str | None = None,
) -> Tuple[Dict[str, str], str]:
    """
    Build payload gửi sang SePay checkout/init.
    Trả về (payload, signature) để tiện debug/log.
    """
    def normalize_method(method: str | None) -> str | None:
        if not method:
            return None
        mapping = {
            "ATM": "BANK_TRANSFER",
            "BANK": "BANK_TRANSFER",
            "BANK_TRANSFER": "BANK_TRANSFER",
            "NAPAS": "NAPAS_BANK_TRANSFER",
            "NAPAS_BANK_TRANSFER": "NAPAS_BANK_TRANSFER",
            "CARD": "CARD",
        }
        return mapping.get(str(method).upper(), str(method).upper())

    payload: Dict[str, str] = {
        "merchant": merchant_id,
        "currency": currency,
        "order_amount": str(int(amount)),  # SePay yêu cầu VND số nguyên
        "operation": operation,
        "order_description": description,
    }

    norm_method = normalize_method(payment_method)
    if norm_method:
        payload["payment_method"] = norm_method

    payload["order_invoice_number"] = str(invoice_id)

    if customer_id:
        payload["customer_id"] = customer_id
    if success_url:
        payload["success_url"] = success_url
    if error_url:
        payload["error_url"] = error_url
    if cancel_url:
        payload["cancel_url"] = cancel_url

    # Tính chữ ký theo chuẩn SePay
    payload["signature"] = sign_checkout(payload, secret_key)
    return payload, payload["signature"]


def create_checkout(
    checkout_url: str,
    payload: Dict[str, str],
    timeout: float = 10.0,
    follow_redirects: bool = False,
) -> Dict:
    """
    Gửi form-POST tới endpoint checkout (SePay yêu cầu form data).
    Nếu server trả JSON sẽ parse, còn nếu trả HTML/redirect, trả text/status để tiện debug.
    """
    with httpx.Client(timeout=timeout, follow_redirects=follow_redirects) as client:
        resp = client.post(
            checkout_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        ctype = resp.headers.get("content-type", "")
        if "application/json" in ctype:
            return resp.json()
        return {
            "status_code": resp.status_code,
            "content_type": ctype,
            "text": resp.text,
        }
