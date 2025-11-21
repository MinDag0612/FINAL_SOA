from pydantic import BaseModel

class User_infor(BaseModel):
    fullname: str
    email: str
    role: str

class New_User_infor(BaseModel):
    fullname: str
    email: str
    role: str
    password: str
    
class LoginRequest(BaseModel):
    email: str
    password: str

