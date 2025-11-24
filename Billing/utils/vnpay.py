import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Tuple


def vnp_encode(value: str) -> str:
    """Encode string theo chuẩn VNPay (dùng + cho khoảng trắng)."""
    return urllib.parse.quote_plus(value, safe="")


def build_payment_url(
    base_url: str,
    tmn_code: str,
    hash_secret: str,
    amount: float,
    txn_ref: str,
    order_info: str,
    ip_addr: str,
    return_url: str,
    expire_minutes: int = 15,
    locale: str = "vn",
    curr_code: str = "VND",
    order_type: str = "other",
    bank_code: str | None = None,
    ipn_url: str | None = None,
    time_offset_seconds: int = 0,
) -> Tuple[str, Dict[str, str]]:

    amount_vnp = int(amount * 100)
    now = datetime.now() + timedelta(seconds=time_offset_seconds)

    params: Dict[str, str] = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": tmn_code,
        "vnp_Amount": str(amount_vnp),
        "vnp_CurrCode": curr_code,
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": order_info,
        "vnp_OrderType": order_type,
        "vnp_Locale": locale,
        "vnp_ReturnUrl": return_url,
        "vnp_IpAddr": ip_addr,
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": (now + timedelta(minutes=expire_minutes)).strftime("%Y%m%d%H%M%S"),
    }

    if bank_code:
        params["vnp_BankCode"] = bank_code
    if ipn_url:
        params["vnp_IpnUrl"] = ipn_url

    # --- SIGNATURE STEP ---
    sorted_items = sorted(params.items())
    sign_data = "&".join(f"{k}={vnp_encode(str(v))}" for k, v in sorted_items)

    signature = hmac.new(
        hash_secret.encode(),
        sign_data.encode(),
        hashlib.sha512
    ).hexdigest()

    query_string = sign_data
    final_url = (
        f"{base_url}?{query_string}"
        f"&vnp_SecureHashType=HmacSHA512&vnp_SecureHash={signature}"
    )

    print("VNP SIGN DATA:", sign_data)
    print("VNP SIGNATURE:", signature)
    print("VNP URL:", final_url)

    return final_url, params


def verify_response(params: Dict[str, str], hash_secret: str) -> bool:
    secure_hash = params.get("vnp_SecureHash")
    if not secure_hash:
        return False

    sorted_items = sorted(
        (k, v) for k, v in params.items()
        if k not in ("vnp_SecureHash", "vnp_SecureHashType")
    )

    sign_data = "&".join(f"{k}={vnp_encode(str(v))}" for k, v in sorted_items)

    computed = hmac.new(
        hash_secret.encode(),
        sign_data.encode(),
        hashlib.sha512
    ).hexdigest()

    return computed == secure_hash
