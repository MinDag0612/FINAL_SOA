from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from core.connDB import connDB
from models.court_models import CourtCreate, CourtUpdate
from repository.court_repo import CourtRepo
from service.court_service import CourtService

app = FastAPI()
db = connDB()


def get_court_service(session: Session = Depends(db.get_db)) -> CourtService:
    return CourtService(CourtRepo(session))


@app.get("/health")
def health_check():
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
    updated = service.update_court(court_id, payload)
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

