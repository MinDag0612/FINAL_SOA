from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from core.connDB import connDB
from models.court_models import (
    CourtAvailabilityRequest,
    CourtCreate,
    CourtUpdate,
)
from service.court_service import CourtService

app = FastAPI()
db = connDB()


def get_service() -> CourtService:
    return CourtService()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "court"}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/court")
def list_courts(service: CourtService = Depends(get_service)):
    return {"status": "success", "data": service.list_courts()}


@app.post("/court")
def create_court(
    payload: CourtCreate,
    service: CourtService = Depends(get_service),
    session: Session = Depends(db.get_db),
):
    return {"status": "success", "data": service.create_court(payload)}


@app.get("/court/{court_id}")
def get_court(court_id: int, service: CourtService = Depends(get_service)):
    return {"status": "success", "data": service.get_court(court_id)}


@app.put("/court/{court_id}")
def update_court(
    court_id: int,
    payload: CourtUpdate,
    service: CourtService = Depends(get_service),
):
    return service.update_court(court_id, payload)


@app.delete("/court/{court_id}")
def delete_court(court_id: int, service: CourtService = Depends(get_service)):
    return service.delete_court(court_id)


@app.get("/court/{court_id}/availability")
def get_availability(
    court_id: int,
    params: CourtAvailabilityRequest = Depends(),
    service: CourtService = Depends(get_service),
):
    return {"status": "success", "data": service.get_availability(court_id, params)}
