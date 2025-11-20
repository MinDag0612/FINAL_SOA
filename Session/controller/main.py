from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session as SQLASession

from core.connDB import connDB
from models.session_models import SessionCreate
from service.session_service import SessionService

app = FastAPI()
db = connDB()


def get_service() -> SessionService:
    return SessionService()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "session"}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")


@app.post("/session")
def create_session(
    payload: SessionCreate,
    service: SessionService = Depends(get_service),
    session: SQLASession = Depends(db.get_db),
):
    return {"status": "success", "data": service.create_session(payload)}


@app.get("/session/user/{user_id}")
def list_sessions(user_id: int, service: SessionService = Depends(get_service)):
    return {"status": "success", "data": service.list_by_user(user_id)}


@app.delete("/session/{session_id}")
def delete_session(session_id: int, service: SessionService = Depends(get_service)):
    return service.delete_session(session_id)
