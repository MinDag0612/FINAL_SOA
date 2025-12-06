from fastapi import Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session

from Court.core.connDB import connDB
from Court.models.court_models import (
    CourtAvailabilityRequest,
    CourtCreate,
    CourtUpdate,
)
from Court.repository.court_repository import CourtRepository
from Court.service.court_service import CourtService
from jwt_shared.dependencies import get_current_user

app = FastAPI()
db = connDB()

def get_court_service(session: Session = Depends(db.get_db)) -> CourtService:
    return CourtService(CourtRepository(session))


@app.get("/health")
def health_check(user_info: dict = Depends(get_current_user)):
    return {"status": "ok", "service": "court"}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/court")
def list_courts(service: CourtService = Depends(get_court_service)):
    return {"status": "success", "data": service.list_courts()}


@app.post("/court")
def create_court(
    payload: CourtCreate,
    service: CourtService = Depends(get_court_service),
):
    return {"status": "success", "data": service.create_court(payload)}


#------------------FOR MANAGER FLOW (MUST BE BEFORE /{court_id})----------------------------------
@app.get("/manager/{facility_id}/courts")
def get_courts_by_facility(
    facility_id: int,
    service: CourtService = Depends(get_court_service),
    user_info: dict = Depends(get_current_user),
):
    """Get courts by facility - Managers see all, Staff see only assigned courts"""
    role = user_info.get("infor", {}).get("role")
    user_id = int(user_info.get("sub"))
    
    if role not in ["manager", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: managers and staff only",
        )

    try:
        if role == "manager":
            # Manager sees all courts in facility
            courts = service.get_courts_by_facility(facility_id)
        else:  # staff
            # Staff only sees their assigned courts in this facility
            all_staff_courts = service.get_staff_courts(user_id)
            courts = [c for c in all_staff_courts if c.facility_id == facility_id]
        
        return {
            "status": "success",
            "data": {"facility_id": facility_id, "courts": courts},
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load courts: {exc}",
        )


@app.get("/court/{court_id}")
def get_court(court_id: int, service: CourtService = Depends(get_court_service)):
    return {"status": "success", "data": service.get_court(court_id)}


@app.put("/court/{court_id}")
def update_court(
    court_id: int,
    payload: CourtUpdate,
    service: CourtService = Depends(get_court_service),
    user_info: dict = Depends(get_current_user),
):
    """Update court info - accessible by MANAGER and STAFF"""
    role = user_info.get("infor", {}).get("role")
    user_id = int(user_info.get("sub"))
    
    # Manager has full access
    if role == "manager":
        return service.update_court(court_id, payload)
    
    # Staff can only edit their assigned courts
    elif role == "staff":
        if not service.check_staff_can_access_court(user_id, court_id):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You don't have permission to edit this court"
            )
        return service.update_court(court_id, payload)
    
    else:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: Only managers and staff can edit courts"
        )


@app.delete("/court/{court_id}")
def delete_court(court_id: int, service: CourtService = Depends(get_court_service)):
    return service.delete_court(court_id)


@app.get("/court/{court_id}/availability")
def get_availability(
    court_id: int,
    params: CourtAvailabilityRequest = Depends(),
    service: CourtService = Depends(get_court_service),
):
    return {"status": "success", "data": service.get_availability(court_id, params)}


#------------------FOR STAFF FLOW----------------------------------
@app.get("/staff/courts")
def get_staff_courts(
    service: CourtService = Depends(get_court_service),
    user_info: dict = Depends(get_current_user),
):
    """Get all courts assigned to the current staff member"""
    role = user_info.get("infor", {}).get("role")
    if role != "staff":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: Staff only"
        )
    
    staff_id = int(user_info.get("sub"))
    courts = service.get_staff_courts(staff_id)
    return {"status": "success", "data": courts}


@app.post("/staff/{staff_id}/assign-court/{court_id}")
def assign_court_to_staff(
    staff_id: int,
    court_id: int,
    service: CourtService = Depends(get_court_service),
    user_info: dict = Depends(get_current_user),
):
    """Assign a court to a staff member (Manager only)"""
    role = user_info.get("infor", {}).get("role")
    if role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: Managers only"
        )
    
    from Court.repository.court_repository import CourtRepository
    from sqlalchemy.orm import Session
    repo = CourtRepository(next(db.get_db()))
    success = repo.assign_court_to_staff(staff_id, court_id)
    
    if success:
        return {"status": "success", "message": f"Court {court_id} assigned to staff {staff_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to assign court")


#------------------PRICE HISTORY----------------------------------
@app.get("/court/{court_id}/price-history")
def get_court_price_history(
    court_id: int,
    service: CourtService = Depends(get_court_service),
    user_info: dict = Depends(get_current_user),
):
    """Get price change history and schedules for a court (Manager and Staff)"""
    role = user_info.get("infor", {}).get("role")
    user_id = int(user_info.get("sub"))
    
    if role not in ["manager", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: Managers and staff only"
        )
    
    # Check staff access
    if role == "staff" and not service.check_staff_can_access_court(user_id, court_id):
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: You don't have permission to view this court's price history"
        )
    
    return {"status": "success", "data": service.get_price_history(court_id)}
    
    
    
    
    
