from fastapi import Depends, FastAPI, HTTPException, Header, Request
from sqlalchemy.orm import Session

from Court.core.connDB import connDB
from Court.models.court_models import (
    CourtAvailabilityRequest,
    CourtCreate,
    CourtUpdate,
)
from Court.repository.court_repository import CourtRepository
from Court.service.court_service import CourtService
from jwt_shared.jwt import jwt_services

app = FastAPI()
db = connDB()

jwt_services = jwt_services()

url = {
    "facility_service": "http://facility_api:8005"
}

def get_current_user(token: str = Depends(jwt_services.oauth2_scheme)):
    try:
        payload = jwt_services.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload  # hoặc chỉ return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e) + " Invalid token")


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

#------------------FOR MANAGER FLOW----------------------------------

@app.get("/manager/court_by_facility/{facility_id}")
def get_courts_by_facility(
    facility_id: str,
    service: CourtService = Depends(get_court_service),
    user_info: dict = Depends(get_current_user),

    token: str = Header(None, alias="Authorization")
):
    role = user_info["infor"]["role"]
    user_id = user_info["sub"]
    
    try:
        if role != "manager":
            raise HTTPException(status_code=403, detail="Access forbidden: Managers only ")
        courts = service.get_courts_by_facility(facility_id, user_id, token)
        return {"status": "success", "data": courts}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail + " -- from court controller")
    
    
    
    
    
