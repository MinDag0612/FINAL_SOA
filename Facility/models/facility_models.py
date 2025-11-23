from typing import Optional
from pydantic import BaseModel


class FacilityBase(BaseModel):
    facility_name: str
    user_id: int
    location: Optional[str] = None
    sport: Optional[str] = "Badminton"
    amenities: Optional[list[str]] = None
    description: Optional[str] = None


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    facility_name: Optional[str] = None
    user_id: Optional[int] = None
    location: Optional[str] = None
    sport: Optional[str] = None
    amenities: Optional[list[str]] = None
    description: Optional[str] = None


class Facility(FacilityBase):
    facility_id: int
