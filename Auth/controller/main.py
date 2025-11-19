from fastapi import FastAPI, HTTPException, status, Depends


from core.connDB import connDB
from sqlalchemy.orm import Session
from models.auth_models import User_infor, LoginRequest
from service.auth_ser import AuthService
from repository.auth_repo import AuthRepo

app = FastAPI()
db = connDB()

@app.get("/test")
def test():
    return {"message": "Auth service is running"}


@app.get("/db-test")
def db_test():
    result = db.test_query()
    if result:
        return {"status": "success", "message": "Database connection successful", "result": result[0]}
    raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/login")
def create_user(login_infor: LoginRequest, db_session: Session = Depends(db.get_db)):
    auth_service = AuthService(db_session)
    
    email = login_infor.email
    password = login_infor.password
    try:
        if email is None or password is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")
        
        user, response = auth_service.login_user(email, password)
        return {"user": user.__dict__, "response": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))