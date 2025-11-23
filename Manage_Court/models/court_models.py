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


class AvailabilityRequest(BaseModel):
    date: str  # YYYY-MM-DD
    start: str = "06:00"
    end: str = "22:00"
    slot_minutes: int = 60


class Slot(BaseModel):
    start: str
    end: str


class MaintenanceBase(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    reason: Optional[str] = None
    status: Optional[str] = "scheduled"


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceEntry(MaintenanceBase):
    maintenance_id: int
    court_id: int
