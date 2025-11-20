from typing import Optional
from pydantic import BaseModel


class SessionCreate(BaseModel):
    user_id: int
    device: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SessionInfo(SessionCreate):
    session_id: int
    is_active: bool = True


class SessionDeleteResponse(BaseModel):
    session_id: int
    message: str
