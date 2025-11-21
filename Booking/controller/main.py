from fastapi import Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy.orm import Session
from jwt_shared.jwt import jwt_services

from Booking.core.connDB import connDB
from Booking.models.booking_models import (
    BookingCancelRequest,
    BookingCreate,
    BookingUpdate,
    PaymentStatusUpdate,
)
from Booking.service.booking_service import BookingService

app = FastAPI()

jwt_services = jwt_services()

def get_current_user(token: str = Depends(jwt_services.oauth2_scheme)):
    try:
        payload = jwt_services.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload  # hoặc chỉ return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


db = connDB()



def get_service() -> BookingService:
    return BookingService()


@app.get("/health")
def health_check(user: dict = Depends(get_current_user)):
    return {
        "status": "ok",
        "service": "booking",
        "user": user}



@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/booking")
def list_bookings(service: BookingService = Depends(get_service)):
    return {"status": "success", "data": service.list_bookings()}


@app.post("/booking")
def create_booking(
    payload: BookingCreate,
    service: BookingService = Depends(get_service),
    session: Session = Depends(db.get_db),
):
    return {"status": "success", "data": service.create_booking(payload)}


@app.get("/booking/{booking_id}")
def get_booking(booking_id: int, service: BookingService = Depends(get_service)):
    return {"status": "success", "data": service.get_booking(booking_id)}


@app.put("/booking/{booking_id}")
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    service: BookingService = Depends(get_service),
):
    return service.update_booking(booking_id, payload)


@app.post("/booking/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    payload: BookingCancelRequest,
    service: BookingService = Depends(get_service),
):
    return service.cancel_booking(booking_id, payload)


@app.post("/booking/{booking_id}/payment-status")
def payment_callback(
    booking_id: int,
    payload: PaymentStatusUpdate,
    service: BookingService = Depends(get_service),
):
    return service.update_payment_status(booking_id, payload)
