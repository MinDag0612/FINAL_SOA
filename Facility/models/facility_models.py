from typing import List, Optional
from pydantic import BaseModel


class FacilityBase(BaseModel):
    name: str
    address: str
    description: Optional[str] = None
    opening_hours: Optional[str] = None
    contact_phone: Optional[str] = None


class FacilityCreate(FacilityBase):
    amenities: List[str] = []


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    opening_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    amenities: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Facility(FacilityBase):
    facility_id: int
    amenities: List[str] = []
    is_active: bool = True
