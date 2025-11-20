from typing import List
from models.notification_models import (
    BookingConfirmedPayload,
    NotificationLog,
    NotificationSendRequest,
    ReminderPayload,
)


class NotificationService:
    """Stub notification service."""

    def __init__(self):
        self._log = NotificationLog(
            notification_id=1,
            user_email="demo@example.com",
            channel="email",
            status="sent",
            sent_at="2024-06-20T08:00:00Z",
        )

    def send_custom(self, payload: NotificationSendRequest) -> dict:
        return {
            "status": "queued",
            "channels": payload.channels,
            "recipients": payload.recipients,
            "message": "Stub send – chưa kết nối dịch vụ email",
        }

    def booking_confirmed(self, payload: BookingConfirmedPayload) -> dict:
        return {
            "status": "queued",
            "message": f"Notification stub cho booking {payload.booking_id}",
        }

    def reminder(self, payload: ReminderPayload) -> dict:
        return {
            "status": "queued",
            "message": f"Notification nhắc lịch {payload.booking_id}",
        }

    def logs(self, user_email: str, limit: int = 10) -> List[NotificationLog]:
        return [
            self._log.copy(update={"notification_id": idx + 1, "user_email": user_email})
            for idx in range(min(limit, 3))
        ]
