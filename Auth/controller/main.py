from fastapi import FastAPI, HTTPException, status, Depends

from Auth.core.connDB import connDB
from sqlalchemy.orm import Session
from Auth.models.auth_models import User_infor, LoginRequest
from Auth.service.auth_ser import AuthService
from Auth.repository.auth_repo import AuthRepo
from jwt_shared.jwt import jwt_services
from fastapi.security import OAuth2PasswordRequestForm
from jwt_shared.jwt_models import Token
from typing import Annotated
from Auth.models.auth_models import New_User_infor
from Auth.message import send_event

app = FastAPI()

db = connDB()
jwt_services = jwt_services()

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db_session: Session = Depends(db.get_db)):
    user, _, _ = AuthService(db_session).login_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = jwt_services.create_access_token(
        data={"sub": str(user['user_id'])}
    )
    return {"access_token": access_token, "token_type": "bearer"}

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
        
        user, token, response = auth_service.login_user(email, password)
        
        return {
            "user": user,
            "token": token,
            "response": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@app.post("/register")
def register_user(user_infor: New_User_infor, db_session: Session = Depends(db.get_db)):
    auth_service = AuthService(db_session)
    try:
        if not user_infor.email or not user_infor.password or not user_infor.fullname or not user_infor.role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fullname, email, and password and role are required")
        
        if user_infor.role not in ["manager", "customer"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be either 'manager' or 'customer'")
        
        response = auth_service.create_user(user_infor)
        send_event("user.signup", {
            "email": user_infor.email,
            "fullname": user_infor.fullname,
            "role": user_infor.role
        })
        return {
            "response": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e) + " -- from main controller")
        
        