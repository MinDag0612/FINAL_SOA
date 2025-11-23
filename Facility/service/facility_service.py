from typing import List
from fastapi import HTTPException

from Facility.models.facility_models import Facility, FacilityCreate, FacilityUpdate
from Facility.repository.facility_repository import FacilityRepository


class FacilityService:
    """Business logic for facility CRUD."""

    def __init__(self, repo: FacilityRepository):
        self.repo = repo

    def list_facilities(self) -> List[Facility]:
        return self.repo.list_facilities()

    def create_facility(self, payload: FacilityCreate) -> Facility:
        return self.repo.create_facility(payload)

    def get_facility(self, facility_id: int) -> Facility:
        facility = self.repo.get_facility(facility_id)
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")
        return facility

    def update_facility(self, facility_id: int, payload: FacilityUpdate) -> Facility:
        facility = self.repo.update_facility(facility_id, payload)
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")
        return facility

    def delete_facility(self, facility_id: int) -> dict:
        deleted = self.repo.delete_facility(facility_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Facility not found")
        return {"facility_id": facility_id, "message": "Facility deactivated"}
