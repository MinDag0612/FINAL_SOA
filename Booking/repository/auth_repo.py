from sqlalchemy.orm import Session
from sqlalchemy import text
from Booking.core.connDB import connDB


class AuthRepo:
    def __init__(self, db: Session):
        self.db = db
        
    def insert_user(self, user_data: User_infor):
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
                    "password": user_data.password,
                    "role": user_data.role,
                }
            )
            
            self.db.commit() 
            
            return result.rowcount 
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"{e} -- from auth repository")

        
        
        