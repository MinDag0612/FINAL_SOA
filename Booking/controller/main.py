from fastapi import FastAPI, HTTPException, status, Depends

# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from core.connDB import connDB
from sqlalchemy.orm import Session
from models.auth_models import User_infor
from service.auth_ser import AuthService
from repository.auth_repo import AuthRepo

app = FastAPI()
db = connDB()

@app.get("/test")
def test():
    return {"message": "Controller service is running"}


@app.get("/db-test")
def db_test():
    if db.test_query():
        return {"status": "success", "message": "Database connection successful"}
    raise HTTPException(status_code=500, detail="Database connection failed")
    

# @app.post("/insert-user")
# def insert_user(user: User_infor, db: Session = Depends(db.get_db)):
#     auth_service = AuthService(db)
#     result = auth_service.create_user(user)
#     if (result):
#         return {"status": "success", "message": "User created successfully"}
#     raise HTTPException(status_code=500, detail="User creation failed")