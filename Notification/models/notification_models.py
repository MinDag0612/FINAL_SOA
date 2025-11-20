from typing import List, Optional
from pydantic import BaseModel, EmailStr


class NotificationSendRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    message: str
    channels: List[str] = ["email"]


class BookingConfirmedPayload(BaseModel):
    booking_id: int
    user_email: EmailStr
    scheduled_time: str
    court_name: str


class ReminderPayload(BaseModel):
    booking_id: int
    user_email: EmailStr
    reminder_time: str
    note: Optional[str] = None


class NotificationLog(BaseModel):
    notification_id: int
    user_email: EmailStr
    channel: str
    status: str
    sent_at: str
