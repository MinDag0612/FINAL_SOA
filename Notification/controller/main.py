from fastapi import Depends, FastAPI, Query, HTTPException, Body
from Notification.models.notification_models import (
    BookingConfirmedPayload,
    NotificationSendRequest,
    ReminderPayload,
)
from Notification.service.notification_service import NotificationService
from fastapi.exceptions import HTTPException as HttpException
from jwt_shared.jwt import jwt_services
import json, threading
from Notification.message import consume_messages

app = FastAPI()

jwt_services = jwt_services()

def get_current_user(token: str = Depends(jwt_services.oauth2_scheme)):
    try:
        payload = jwt_services.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload  # hoặc chỉ return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e) + " Invalid token")


def get_service() -> NotificationService:
    return NotificationService()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notification"}

@app.post("/notification/send-email-verify-register")
def send_email_verify_register(
    service: NotificationService = Depends(get_service),
    user: dict = Body(...)
    ):
    # return user
    try:
        return service.send_email_verify_register(user), {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) + "-- from notification controller")
    
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

