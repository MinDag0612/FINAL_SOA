from fastapi import Depends, FastAPI, HTTPException
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
    role = user_info.get("infor", {}).get("role")
    if role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: managers only",
        )

    try:
        courts = service.get_courts_by_facility(facility_id)
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
):
    return service.update_court(court_id, payload)


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

