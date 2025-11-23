from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from core.connDB import connDB
from models.court_models import (
    AvailabilityRequest,
    CourtCreate,
    CourtUpdate,
    MaintenanceCreate,
)
from repository.court_repo import CourtRepo
from repository.maintenance_repo import MaintenanceRepo
from service.court_service import CourtService
from service.facility_client import FacilityClient

app = FastAPI()
db = connDB()


def get_court_service(session: Session = Depends(db.get_db)) -> CourtService:
    return CourtService(CourtRepo(session), MaintenanceRepo(session), FacilityClient())


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "court"}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/court")
def list_courts(
    service: CourtService = Depends(get_court_service),
    facility_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return {
        "status": "success",
        "data": service.list_courts(
            facility_id=facility_id, limit=limit, offset=offset
        ),
    }


@app.post("/court")
def create_court(
    payload: CourtCreate,
    service: CourtService = Depends(get_court_service),
):
    try:
        return {"status": "success", "data": service.create_court(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/court/{court_id}")
def get_court(court_id: int, service: CourtService = Depends(get_court_service)):
    court = service.get_court(court_id)
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")
    return {"status": "success", "data": court}


@app.put("/court/{court_id}")
def update_court(
    court_id: int,
    payload: CourtUpdate,
    service: CourtService = Depends(get_court_service),
):
    try:
        updated = service.update_court(court_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not updated:
        raise HTTPException(status_code=404, detail="Court not found")
    return {"status": "success", "data": updated}


@app.delete("/court/{court_id}")
def delete_court(
    court_id: int, service: CourtService = Depends(get_court_service)
):
    deleted = service.delete_court(court_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Court not found")
    return {"status": "success", "message": "Court deleted"}


@app.get("/court/{court_id}/availability")
def get_availability(
    court_id: int,
    params: AvailabilityRequest = Depends(),
    service: CourtService = Depends(get_court_service),
):
    if not service.get_court(court_id):
        raise HTTPException(status_code=404, detail="Court not found")
    slots = service.get_availability(court_id, params)
    return {"status": "success", "data": slots}


@app.get("/court/{court_id}/maintenance")
def list_maintenance(
    court_id: int,
    date: str = Query(..., description="YYYY-MM-DD"),
    service: CourtService = Depends(get_court_service),
):
    if not service.get_court(court_id):
        raise HTTPException(status_code=404, detail="Court not found")
    return {"status": "success", "data": service.list_maintenance(court_id, date)}


@app.post("/court/{court_id}/maintenance")
def create_maintenance(
    court_id: int,
    payload: MaintenanceCreate,
    service: CourtService = Depends(get_court_service),
):
    if not service.get_court(court_id):
        raise HTTPException(status_code=404, detail="Court not found")
    entry = service.create_maintenance(court_id, payload)
    return {"status": "success", "data": entry}
