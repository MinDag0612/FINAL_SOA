from fastapi import Depends, FastAPI, Query
from models.notification_models import (
    BookingConfirmedPayload,
    NotificationSendRequest,
    ReminderPayload,
)
from service.notification_service import NotificationService

app = FastAPI()


def get_service() -> NotificationService:
    return NotificationService()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notification"}


@app.post("/notification/send")
def send_notification(
    payload: NotificationSendRequest,
    service: NotificationService = Depends(get_service),
):
    return service.send_custom(payload)


@app.post("/notification/booking-confirmed")
def booking_confirmed(
    payload: BookingConfirmedPayload,
    service: NotificationService = Depends(get_service),
):
    return service.booking_confirmed(payload)


@app.post("/notification/reminder")
def send_reminder(
    payload: ReminderPayload, service: NotificationService = Depends(get_service)
):
    return service.reminder(payload)


@app.get("/notification/logs")
def get_logs(
    user_email: str = Query(..., description="Email người dùng"),
    limit: int = Query(10, ge=1, le=100),
    service: NotificationService = Depends(get_service),
):
    return {"status": "success", "data": service.logs(user_email, limit)}
