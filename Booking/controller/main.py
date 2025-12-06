from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jwt_shared.dependencies import get_current_user

from Booking.core.connDB import connDB
from Booking.models.booking_models import (
    BookingActionLog,
    BookingCancelRequest,
    BookingCreate,
    BookingRescheduleRequest,
    BookingUpdate,
    PaymentStatusUpdate,
)
from Booking.service.booking_service import BookingService

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def get_staff_assigned_court_ids(user_id: int) -> list:
    """Get list of court IDs assigned to staff member"""
    import httpx
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(
                f"http://court_service:8004/staff/courts",
                headers={"Authorization": f"Bearer {user_id}"}  # simplified - should pass actual token
            )
            if resp.status_code == 200:
                courts = resp.json().get("data", [])
                return [c["court_id"] for c in courts]
    except Exception:
        pass
    return []


@app.get("/booking")
def list_bookings(
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
    all: bool = Query(False, description="If true, return all confirmed bookings (for checking occupied slots)")
):
    role = user.get("infor", {}).get("role")
    
    # If 'all' parameter is true, return all bookings (customer needs to see all occupied slots)
    if all:
        bookings = service.list_bookings(user_id=None)
        # Don't filter by status - return all bookings so customer can see occupied slots
    else:
        # Normal behavior: manager sees all, others see only their own
        user_id = None if role == "manager" else int(user["sub"])
        bookings = service.list_bookings(user_id=user_id)
    
    # Filter bookings for staff - only show bookings for their assigned courts
    if role == "staff":
        staff_court_ids = get_staff_assigned_court_ids(int(user["sub"]))
        filtered_bookings = []
        for booking in bookings:
            # Check if any booking item is for staff's assigned courts
            has_access = any(
                item.court_id in staff_court_ids 
                for item in booking.items
            )
            if has_access:
                filtered_bookings.append(booking)
        bookings = filtered_bookings
    
    return {"status": "success", "data": bookings}


@app.post("/booking")
def create_booking(
    payload: BookingCreate,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    payload_with_user = payload.model_copy(update={"user_id": int(user["sub"])})
    user_role = user.get("infor", {}).get("role", "customer")
    return {"status": "success", "data": service.create_booking(payload_with_user, user["infor"]["email"], user_role=user_role)}


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
    
@app.get("/facility/{facility_id}/occupied-slots")
def get_occupied_slots(
    facility_id: int,
    date: Optional[str] = Query(None),
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    """Public endpoint for customers to see occupied time slots (confirmed bookings only)"""
    bookings = service.get_bookings_by_facility(facility_id, date)
    # Only return confirmed bookings to show occupied slots
    confirmed_bookings = [b for b in bookings if b.status == "confirmed"]
    return {"status": "success", "data": confirmed_bookings}

@app.get("/manager/{facility_id}/bookings")
def get_bookings_by_facility(
    facility_id: int,
    date: Optional[str] = Query(None),
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    """Get bookings by facility - Manager sees all, Staff sees only assigned courts"""
    role = user.get("infor", {}).get("role")
    
    if role not in ["manager", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: managers and staff only"
        )
    
    bookings = service.get_bookings_by_facility(facility_id, date)
    
    # Filter for staff - only show bookings for their assigned courts
    if role == "staff":
        staff_court_ids = get_staff_assigned_court_ids(int(user["sub"]))
        filtered_bookings = []
        for booking in bookings:
            has_access = any(
                item.court_id in staff_court_ids 
                for item in booking.items
            )
            if has_access:
                filtered_bookings.append(booking)
        bookings = filtered_bookings
    
    return {"status": "success", "data": bookings}


@app.get("/booking/search-by-timeslot")
def search_by_timeslot(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    start_time: str = Query(..., description="Start time in HH:MM format"),
    end_time: str = Query(..., description="End time in HH:MM format"),
    facility_id: Optional[int] = Query(None, description="Optional facility filter"),
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    """
    Search bookings by timeslot and return aggregated counts.
    Accessible by managers and staff (staff see only their assigned courts).
    """
    role = user.get("infor", {}).get("role")
    
    if role not in ["manager", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: managers and staff only"
        )
    
    result = service.search_by_timeslot(date, start_time, end_time, facility_id)
    
    # Filter for staff - only show courts they have access to
    if role == "staff":
        staff_court_ids = get_staff_assigned_court_ids(int(user["sub"]))
        filtered_breakdown = [
            court for court in result.get("courts_breakdown", [])
            if court["court_id"] in staff_court_ids
        ]
        result["courts_breakdown"] = filtered_breakdown
        result["total_bookings"] = sum(c["booking_count"] for c in filtered_breakdown)
        result["total_players"] = result["total_bookings"]
    
    return {
        "status": "success",
        "data": {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "total_bookings": result["total_bookings"],
            "total_players": result["total_players"],
            "courts_breakdown": result["courts_breakdown"]
        }
    }


@app.get("/booking/{booking_id}")
def get_booking(
    booking_id: int,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    user_id = None if role in ["manager", "staff"] else int(user["sub"])
    
    booking = service.get_booking(booking_id, user_id=user_id)
    
    # Check staff access
    if role == "staff":
        staff_court_ids = get_staff_assigned_court_ids(int(user["sub"]))
        has_access = any(item.court_id in staff_court_ids for item in booking.items)
        if not has_access:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: This booking is not for your assigned courts"
            )
    
    return {"status": "success", "data": booking}


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


@app.post("/booking/{booking_id}/reschedule")
def reschedule_booking(
    booking_id: int,
    payload: BookingRescheduleRequest,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    if role not in ["manager", "staff"]:
        raise HTTPException(status_code=403, detail="Chỉ quản lý/nhân viên mới được chỉnh sửa booking.")
    try:
        booking = service.reschedule_booking(
            booking_id=booking_id,
            payload=payload,
            user_id=int(user["sub"]),
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"status": "success", "data": booking}


@app.post("/booking/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    payload: BookingCancelRequest,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    user_id = int(user["sub"])
    return service.cancel_booking(booking_id, payload, user_id=user_id, user_role=role)


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


@app.get("/logs/{booking_id}")
def get_booking_logs_by_id(
    booking_id: int,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    """Get all logs for a specific booking (for booking detail view)"""
    logs = service.get_booking_logs_by_id(booking_id)
    return {"status": "success", "data": logs}


@app.get("/facility/{facility_id}/logs")
def get_facility_booking_logs(
    facility_id: int,
    date: Optional[str] = Query(None, description="Date filter in YYYY-MM-DD"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    """Get booking logs for a facility (for manager history view)"""
    role = user.get("infor", {}).get("role")
    if role not in ["manager", "staff"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    logs = service.get_facility_booking_logs(facility_id, date, limit)
    
    # Filter by staff's assigned courts if needed
    if role == "staff":
        staff_court_ids = get_staff_assigned_court_ids(int(user["sub"]))
        # Note: logs might not have court_id directly, need to fetch from booking_items
        # For now, staff can see all logs for their facility
    
    return {"status": "success", "data": logs}
    return {"status": "success", "data": logs}


@app.post("/booking/{booking_id}/log")
def log_booking_action(
    booking_id: int,
    payload: BookingActionLog,
    service: BookingService = Depends(get_service),
    user: dict = Depends(get_current_user),
):
    role = user.get("infor", {}).get("role")
    if role not in ["manager", "staff"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    user_id = None if role == "manager" else int(user["sub"])
    service.log_booking_action(
        booking_id,
        payload.action,
        payload.note,
        user_id=user_id,
        role=role,
    )
    return {"status": "success", "message": "Log recorded"}
