from sqlalchemy.orm import Session
from Auth.models.auth_models import New_User_infor
from sqlalchemy import text
from Auth.core.connDB import connDB


class AuthRepo:
    def __init__(self, db: Session):
        self.db = db
        
    def insert_user(self, user_data: New_User_infor, password_hashed: str):
        query = text(
            """
            INSERT INTO User_Infor (fullname, email, password, role)
            VALUES (:fullname, :email, :password, :role)
            """
        )
        try:
            result = self.db.execute(
                query,
                {
                    "fullname": user_data.fullname,
                    "email": user_data.email,
                    "password": password_hashed,
                    "role": user_data.role,
                }
            )
            
            self.db.commit() 
            
            return result 
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"{e} -- from auth repository")
        
    def get_user_by_email(self, email: str):
        query = text(
            """
            SELECT * FROM User_Infor
            WHERE email = :email
            LIMIT 1
            """
        )
        try:
            result = self.db.execute(query, {"email": email})
            user_row = result.fetchone()
            if user_row is None:
                return None
            return user_row._asdict()
        except Exception as e:
            raise Exception(f"{e} -- from auth repository")
        
    def get_user_by_id(self, user_id: str):
        query = text(
            "SELECT * FROM User_Infor WHERE user_id = :user_id LIMIT 1"
        )
        try:
            result = self.db.execute(query, {"user_id": user_id})
            user_row = result.fetchone()
            if user_row:
                return user_row._asdict()
            return None
        except Exception as e:
            raise Exception(f"{e} -- from auth repository")