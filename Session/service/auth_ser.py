from sqlalchemy.orm import Session
from models.auth_models import User_infor
from repository.auth_repo import AuthRepo
from service.jwt import jwt_services

class AuthService:
    def __init__(self, db: Session):
        self.repo = AuthRepo(db)
        self.jwt_service = jwt_services()
        
    def create_user(self, user: User_infor):
        try:
            pass_hashed = self.jwt_service.get_hash(user.password)
            new_user = user.copy(update={"password": pass_hashed})
            self.repo.insert_user(new_user)
            return {"status": "success", "message": "User created successfully"}
        except Exception as e:
            raise Exception(f"{e} -- from auth service")