from sqlalchemy.orm import Session
from Auth.models.auth_models import User_infor
from Auth.repository.auth_repo import AuthRepo
from jwt_shared.jwt import jwt_services

class AuthService:
    def __init__(self, db: Session):
        self.repo = AuthRepo(db)
        self.jwt_service = jwt_services()
        
    def login_user(self, email: str, password: str):
        try:
            user = self.repo.get_user_by_email(email)
            if not user:
                raise Exception("User not found")
            password_valid = self.jwt_service.verify_password(password, user['password'])
            if not password_valid:
                raise Exception("Invalid password")
            user.pop('password')  # Remove password before returning
            token_data = {
                "sub": str(user['user_id']),
                "infor": user
            }
            token = self.jwt_service.create_access_token(data=token_data)
            return user, token, {"status": "success", "message": "Login successful"}
        
        except Exception as e:
            raise Exception(f"{e} -- from auth service")
        
    def create_user(self, user: User_infor, password: str):
        try:
            pass_hashed = self.jwt_service.get_hash(user.password)
            new_user = user.copy()
            pass_hashed = self.jwt_service.get_hash(password)
            self.repo.insert_user(new_user, pass_hashed)
            return new_user, {"status": "success", "message": "User created successfully"}
        except Exception as e:
            raise Exception(f"{e} -- from auth service")
        
        
        
    