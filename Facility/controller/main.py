from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from Facility.core.connDB import connDB
from Facility.models.facility_models import FacilityCreate, FacilityUpdate
from Facility.repository.facility_repository import FacilityRepository
from Facility.service.facility_service import FacilityService

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
