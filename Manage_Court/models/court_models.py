from typing import List, Optional
from pydantic import BaseModel


class CourtBase(BaseModel):
    facility_id: int
    name: str
    surface_type: Optional[str] = None
    hourly_rate: Optional[float] = None
    description: Optional[str] = None


class CourtCreate(CourtBase):
    available_hours: List[str] = []


class CourtUpdate(BaseModel):
    facility_id: Optional[int] = None
    name: Optional[str] = None
    surface_type: Optional[str] = None
    hourly_rate: Optional[float] = None
    description: Optional[str] = None
    available_hours: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Court(CourtBase):
    court_id: int
    available_hours: List[str] = []
    is_active: bool = True


class CourtAvailabilityRequest(BaseModel):
    date: str


class CourtAvailability(BaseModel):
    court_id: int
    date: str
    available_slots: List[str]
