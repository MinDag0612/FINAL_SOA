from typing import List, Optional

from models.facility_models import Facility, FacilityCreate, FacilityUpdate
from repository.facility_repo import FacilityRepo


class FacilityService:
\
    def __init__(self, repo: FacilityRepo):
        self.repo = repo

    def list_facilities(self) -> List[Facility]:
        return [Facility(**item) for item in self.repo.list_facilities()]

    def create_facility(self, payload: FacilityCreate) -> Facility:
        record = self.repo.create_facility(payload.model_dump())
        return Facility(**record)

    def get_facility(self, facility_id: int) -> Optional[Facility]:
        record = self.repo.get_facility(facility_id)
        return Facility(**record) if record else None

    def update_facility(
        self, facility_id: int, payload: FacilityUpdate
    ) -> Optional[Facility]:
        record = self.repo.update_facility(
            facility_id, payload.model_dump(exclude_none=True)
        )
        return Facility(**record) if record else None

    def delete_facility(self, facility_id: int) -> bool:
        return self.repo.delete_facility(facility_id)
