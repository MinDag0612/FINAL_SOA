from pydantic import BaseModel

class User_infor(BaseModel):
    fullname: str
    email: str
    role: str
    
class LoginRequest(BaseModel):
    email: str
    password: str