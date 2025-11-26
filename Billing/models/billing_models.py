from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InvoiceCreate(BaseModel):
    booking_id: int
    user_id: int
    amount: float
    currency: str = "VND"
    description: Optional[str] = None


class Invoice(BaseModel):
    invoice_id: int
    booking_id: int
    user_id: int
    amount: float
    currency: str
    status: str


class PaymentRequest(BaseModel):
    method: str
    booking_id: int
    return_url: Optional[str] = None


class PaymentWebhook(BaseModel):
    event: str
    payload: dict


class BillingHistoryParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    limit: int = Field(default=10, ge=1, le=100)


# ===== SePay Models =====

class SePayCreatePaymentRequest(BaseModel):
    """Request to create SePay payment link"""
    booking_id: int
    amount: float
    description: str
    order_code: Optional[str] = None


class SePayPaymentResponse(BaseModel):
    """Response after creating SePay payment"""
    payment_url: Optional[str] = None
    booking_id: int
    amount: float
    merchant_id: str
    status: str = "pending"
    message: Optional[str] = None


class SePayIPNRequest(BaseModel):
    """IPN payload from SePay"""
    model_config = ConfigDict(extra="allow")  # Allow extra fields
    
    merchantId: str
    orderCode: str
    status: str
    transactionId: Optional[str] = None
    signature: str


class SePayReturnRequest(BaseModel):
    """Return URL query params from SePay"""
    status: str
    booking_id: int
    transactionId: Optional[str] = None

