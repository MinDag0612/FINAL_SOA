from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from Facility.core.connDB import connDB
from Facility.models.facility_models import FacilityCreate, FacilityUpdate
from Facility.repository.facility_repository import FacilityRepository
from Facility.service.facility_service import FacilityService
from jwt_shared.dependencies import get_current_user

app = FastAPI()
db = connDB()


def get_facility_service(session: Session = Depends(db.get_db)) -> FacilityService:
    return FacilityService(FacilityRepository(session))


@app.get("/")
def health_check():
    return {"status": "ok", "service": "facility"}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/facility")
def list_facilities(service: FacilityService = Depends(get_facility_service)):
    return {"status": "success", "data": service.list_facilities()}


@app.post("/facility")
def create_facility(
    payload: FacilityCreate,
    service: FacilityService = Depends(get_facility_service),
):
    return {"status": "success", "data": service.create_facility(payload)}


#------------------FOR MANAGER FLOW (MUST BE BEFORE /{facility_id})----------------------------------
@app.get("/manager/facilities")
def get_facilities_by_manager(
    service: FacilityService = Depends(get_facility_service),
    user_info: dict = Depends(get_current_user),
):
    role = user_info.get("infor", {}).get("role")
    if role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: managers only",
        )

    manager_id = user_info.get("sub")
    if not manager_id:
        raise HTTPException(status_code=400, detail="Manager ID not found in token")

    try:
        manager_id_int = int(manager_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Manager ID format")

    try:
        print(f"[Facility Manager] Loading facilities for manager_id={manager_id_int}")
        facilities = service.get_facilities_by_manager(manager_id_int)
        print(f"[Facility Manager] Found {len(facilities)} facilities")
        return {"status": "success", "data": facilities}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Facility Manager Error] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading facilities: {str(e)}",
        )


@app.get("/facility/{facility_id}")
def get_facility(
    facility_id: int, service: FacilityService = Depends(get_facility_service)
):
    return {"status": "success", "data": service.get_facility(facility_id)}


@app.put("/facility/{facility_id}")
def update_facility(
    facility_id: int,
    payload: FacilityUpdate,
    service: FacilityService = Depends(get_facility_service),
):
    return service.update_facility(facility_id, payload)


@app.delete("/facility/{facility_id}")
def delete_facility(
    facility_id: int,
    service: FacilityService = Depends(get_facility_service),
):
    return service.delete_facility(facility_id)
    
