import base64
import hashlib
import hmac
from typing import Dict, Tuple

import httpx


def sign_checkout(data: Dict[str, str], secret_key: str) -> str:
    """
    SePay yêu cầu ký toàn bộ payload (trừ signature) theo thứ tự key alphabet.
    Ghép key=value bằng '&' rồi HMAC-SHA256 và Base64.
    """
    # đảm bảo dùng cùng thứ tự ở backend và form để tránh lệch chữ ký
    sign_data = "&".join(f"{k}={data[k]}" for k in sorted(data.keys()))
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
) -> Tuple[Dict[str, str], str]:
    payload: Dict[str, str] = {
        "merchant": merchant_id,
        "currency": currency,
        "order_amount": str(int(amount)),  # SePay yêu cầu VND số nguyên
        "operation": operation,
        "order_description": description,
        "order_invoice_number": str(invoice_id),
    }
    if payment_method:
        payload["payment_method"] = payment_method
    if success_url:
        payload["success_url"] = success_url
    if error_url:
        payload["error_url"] = error_url
    if cancel_url:
        payload["cancel_url"] = cancel_url

    payload["signature"] = sign_checkout(payload, secret_key)
    return payload, payload["signature"]


def create_checkout(
    checkout_url: str,
    payload: Dict[str, str],
    timeout: float = 10.0,
) -> Dict:
    """
    Gửi form-POST tới endpoint checkout (SePay yêu cầu form data).
    Nếu server trả JSON sẽ parse, còn nếu trả HTML/redirect, trả text/status để tiện debug.
    """
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.post(
            checkout_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "")
        if "application/json" in ctype:
            return resp.json()
        return {"status_code": resp.status_code, "content_type": ctype, "text": resp.text}
