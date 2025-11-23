from typing import List, Optional
from pydantic import BaseModel


class CourtBase(BaseModel):
    facility_id: int
    court_name: str
    price_per_hour: float
    description: Optional[str] = None


class CourtCreate(CourtBase):
    pass


class CourtUpdate(BaseModel):
    facility_id: Optional[int] = None
    court_name: Optional[str] = None
    price_per_hour: Optional[float] = None
    description: Optional[str] = None


class Court(CourtBase):
    court_id: int
