import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

class connDB:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "root")
        self.database = os.getenv("DB_NAME", "DB_BILLING")
        self.port = int(os.getenv("DB_PORT", 3306))
        
        self.DATABASE_URL = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"

        # tạo engine
        self.engine = create_engine(self.DATABASE_URL, echo=True, future=True)

        # session factory
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

        # Base để khai báo ORM models
        self.Base = declarative_base()


    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    def test_query(self):
        db = next(self.get_db())
        try:
            result = db.execute(text("SELECT 1"))
            return result.fetchone()
        finally:
            db.close()
        