from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from Facility.core.connDB import connDB
from Facility.models.facility_models import FacilityCreate, FacilityUpdate
from Facility.repository.facility_repository import FacilityRepository
from Facility.service.facility_service import FacilityService
from jwt_shared.jwt import jwt_services
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
db = connDB()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # hoặc chỉ định domain nào được phép
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jwt_services = jwt_services()

def get_current_user(token: str = Depends(jwt_services.oauth2_scheme)):
    try:
        payload = jwt_services.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload  # hoặc chỉ return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e) + " Invalid token")


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


#------------------FOR MANAGER FLOW----------------------------------
@app.get("/manager/facilities")
def get_facilities_by_manager(
    user_info: dict = Depends(get_current_user),
    service: FacilityService = Depends(get_facility_service)
    ):
    manager_id = user_info.get("sub")
    try:
        facilities = service.get_facilities_by_manager(manager_id)
        return {"status": "success", "data": facilities}
    except HTTPException as e:
        raise {"status": "error", "detail": e.detail + " -- from facility controller"}

@app.get("/manager/user_id_by_facility/{facility_id}")
def get_manager_id_by_facility(
    facility_id: int,  
    user_info: dict = Depends(get_current_user),
    service: FacilityService = Depends(get_facility_service)
    ):
    role = user_info["infor"]["role"]
    if role != "manager":
        raise HTTPException(status_code=403, detail="Access forbidden: Managers only")
    try:
        manager_user_id = service.get_manager_id_by_facility(facility_id)
        return {"status": "success", "user_id": manager_user_id}
    except HTTPException as e:
        raise {"status": "error", "detail": e.detail + " -- from facility controller"}
    
