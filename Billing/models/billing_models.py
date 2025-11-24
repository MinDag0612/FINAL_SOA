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
