from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


BookingStatus = Literal["pending", "confirmed", "cancelled", "completed", "expired"]


class BookingItem(BaseModel):
    item_id: Optional[int] = None
    court_id: int
    start_time: datetime
    end_time: datetime
    price: float


class BookingCreate(BaseModel):
    user_id: Optional[int] = None
    facility_id: int
    items: List[BookingItem]
    payment_method: str = Field(default="cash")
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    note: Optional[str] = None


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    note: Optional[str] = None


class Booking(BaseModel):
    booking_id: int
    status: BookingStatus
    total_amount: float
    user_id: int
    facility_id: int
    items: List[BookingItem]
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    paid_at: Optional[datetime] = None
    note: Optional[str] = None


class BookingCancelRequest(BaseModel):
    reason: Optional[str] = None


class BookingItemUpdate(BaseModel):
    item_id: int
    court_id: int
    start_time: datetime
    end_time: datetime
    price: float


class BookingRescheduleRequest(BaseModel):
    items: List[BookingItemUpdate]
    note: Optional[str] = None


class BookingActionLog(BaseModel):
    action: str
    note: Optional[str] = None


class PaymentStatusUpdate(BaseModel):
    status: Literal["paid", "failed"]
    reference_id: Optional[str] = None
    gateway_payload: Optional[dict] = None
