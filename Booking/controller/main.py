from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from jwt_shared.dependencies import get_current_user

from Booking.core.connDB import connDB
from Booking.models.booking_models import (
    BookingCancelRequest,
    BookingCreate,
    BookingUpdate,
    PaymentStatusUpdate,
)
from Booking.service.booking_service import BookingService

app = FastAPI()

db = connDB()


def get_service(session: Session = Depends(db.get_db)) -> BookingService:
    return BookingService(session)


@app.get("/health")
def health_check(user: dict = Depends(get_current_user)):
    return {"status": "ok", "service": "booking", "user": user}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/booking")
def list_bookings(
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    user_id = None if role == "manager" else int(user["sub"])
    return {"status": "success", "data": service.list_bookings(user_id=user_id)}


@app.post("/booking")
def create_booking(
    payload: BookingCreate,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    payload_with_user = payload.model_copy(update={"user_id": int(user["sub"])})
    return {"status": "success", "data": service.create_booking(payload_with_user, user["infor"]["email"])}


#------------------FOR MANAGER FLOW (MUST BE BEFORE /{booking_id})----------------------------------
@app.get("/manager/{court_id}/time_slots")
def get_time_slots_by_court(
    court_id: int,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    try:
        time_slots = service.get_time_slots_by_court(court_id)
        return {"status": "success", "data": time_slots}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/manager/{facility_id}/bookings")
def get_bookings_by_facility(
    facility_id: int,
    date: Optional[str] = Query(None),
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    bookings = service.get_bookings_by_facility(facility_id, date)
    return {"status": "success", "data": bookings}


@app.get("/booking/{booking_id}")
def get_booking(
    booking_id: int,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    user_id = None if role == "manager" else int(user["sub"])
    return {"status": "success", "data": service.get_booking(booking_id, user_id=user_id)}


@app.put("/booking/{booking_id}")
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    user_id = None if role == "manager" else int(user["sub"])
    return service.update_booking(booking_id, payload, user_id=user_id)


@app.post("/booking/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    payload: BookingCancelRequest,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    user_id = None if role == "manager" else int(user["sub"])
    return service.cancel_booking(booking_id, payload, user_id=user_id)


@app.delete("/booking/{booking_id}")
def delete_booking(
    booking_id: int,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    if role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can delete bookings")
    service.delete_booking(booking_id)
    return {"status": "success"}

@app.post("/booking/{booking_id}/payment-status")
def payment_callback(
    booking_id: int,
    payload: PaymentStatusUpdate,
    service: BookingService = Depends(get_service),
):
    return service.update_payment_status(booking_id, payload)
