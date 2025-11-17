from pydantic import BaseModel

class User_infor(BaseModel):
    fullname: str
    email: str
    password: str
    role: str