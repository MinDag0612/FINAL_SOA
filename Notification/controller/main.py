from fastapi import Depends, FastAPI, Query, HTTPException, Body
from Notification.models.notification_models import (
    BookingConfirmedPayload,
    NotificationSendRequest,
    ReminderPayload,
)
from Notification.service.notification_service import NotificationService
from jwt_shared.dependencies import get_current_user
import json, threading
from Notification.message import consume_messages

app = FastAPI()


def get_service() -> NotificationService:
    return NotificationService()


@app.get("/health")
def health_check(user = Depends(get_current_user)):
    return {"status": "ok", "service": "notification"}

@app.post("/notification/send-email-verify-register")
def send_email_verify_register(
    service: NotificationService = Depends(get_service),
    user: dict = Body(...)
    ):
    try:
        result = service.send_email_verify_register(user)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/notification/send-booking-confirmed")
def send_booking_confirmed(
    service: NotificationService = Depends(get_service),
    booking_infor: BookingConfirmedPayload = None
    ):
    
    try:
        return service.booking_confirmed(booking_infor.__dict__), {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) + "-- from notification controller")


@app.on_event("startup")
def start_kafka_consumer():
    # Chạy consumer trong thread riêng, không block FastAPI
    thread = threading.Thread(target=consume_messages, daemon=True)
    thread.start()

