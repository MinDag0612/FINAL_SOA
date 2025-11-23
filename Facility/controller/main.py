from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from core.connDB import connDB
from models.facility_models import FacilityCreate, FacilityUpdate
from models.equipment_models import EquipmentCreate, EquipmentUpdate
from repository.facility_repo import FacilityRepo
from service.facility_service import FacilityService

app = FastAPI()
db = connDB()


def get_service(session: Session = Depends(db.get_db)) -> FacilityService:
    return FacilityService(FacilityRepo(session))


@app.get("/")
def health_check():
    return {"status": "ok", "service": "facility"}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/facility")
def list_facilities(
    service: FacilityService = Depends(get_service),
):
    return {
        "status": "success",
        "data": service.list_facilities(),
    }


@app.post("/facility")
def create_facility(
    payload: FacilityCreate,
    service: FacilityService = Depends(get_service),
):
    return {"status": "success", "data": service.create_facility(payload)}


@app.get("/facility/{facility_id}")
def get_facility(
    facility_id: int,
    service: FacilityService = Depends(get_service),
):
    facility = service.get_facility(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return {"status": "success", "data": facility}


@app.put("/facility/{facility_id}")
def update_facility(
    facility_id: int,
    payload: FacilityUpdate,
    service: FacilityService = Depends(get_service),
):
    updated = service.update_facility(facility_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Facility not found")
    return {"status": "success", "data": updated}


@app.delete("/facility/{facility_id}")
def delete_facility(
    facility_id: int,
    service: FacilityService = Depends(get_service),
):
    deleted = service.delete_facility(facility_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Facility not found")
    return {"status": "success", "message": "Facility deleted"}
