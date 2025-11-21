from fastapi import Depends, FastAPI, Query, HTTPException
from Notification.models.notification_models import (
    BookingConfirmedPayload,
    NotificationSendRequest,
    ReminderPayload,
)
from Notification.service.notification_service import NotificationService
from fastapi.exceptions import HTTPException as HttpException
from jwt_shared.jwt import jwt_services

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
    user: dict = Depends(get_current_user)
    ):
    # return user
    try:
        return service.send_email_verify_register(user["infor"]), {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) + "-- from notification controller")





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
