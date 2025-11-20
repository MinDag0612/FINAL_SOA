from typing import List, Literal, Optional
from pydantic import BaseModel, Field


BookingStatus = Literal["pending", "confirmed", "cancelled", "completed"]


class BookingItem(BaseModel):
    court_id: int
    start_time: str
    end_time: str
    price: float


class BookingCreate(BaseModel):
    user_id: int
    facility_id: int
    items: List[BookingItem]
    payment_method: str = Field(default="cash")
    note: Optional[str] = None


class BookingUpdate(BaseModel):
    items: Optional[List[BookingItem]] = None
    status: Optional[BookingStatus] = None
    note: Optional[str] = None


class Booking(BaseModel):
    booking_id: int
    status: BookingStatus
    total_amount: float
    user_id: int
    facility_id: int
    items: List[BookingItem]


class BookingCancelRequest(BaseModel):
    reason: Optional[str] = None


class PaymentStatusUpdate(BaseModel):
    status: Literal["paid", "failed"]
    reference_id: Optional[str] = None
    gateway_payload: Optional[dict] = None
