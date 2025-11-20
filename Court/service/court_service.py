from typing import List
from models.court_models import (
    Court,
    CourtAvailability,
    CourtAvailabilityRequest,
    CourtCreate,
    CourtUpdate,
)


class CourtService:
    """Stub court service."""

    def __init__(self):
        self._sample = Court(
            court_id=1,
            facility_id=1,
            name="Sân 1",
            surface_type="PVC",
            hourly_rate=120000,
            description="Sân chuẩn thi đấu, trần cao.",
            available_hours=["06:00", "07:00", "08:00", "09:00"],
            is_active=True,
        )

    def list_courts(self) -> List[Court]:
        return [self._sample]

    def create_court(self, payload: CourtCreate) -> Court:
        return Court(
            court_id=42,
            facility_id=payload.facility_id,
            name=payload.name,
            surface_type=payload.surface_type,
            hourly_rate=payload.hourly_rate,
            description=payload.description,
            available_hours=payload.available_hours,
            is_active=True,
        )

    def get_court(self, court_id: int) -> Court:
        return self._sample.copy(update={"court_id": court_id})

    def update_court(self, court_id: int, payload: CourtUpdate) -> dict:
        return {
            "court_id": court_id,
            "updated_fields": payload.model_dump(exclude_none=True),
            "message": "Stub update – chưa lưu DB",
        }

    def delete_court(self, court_id: int) -> dict:
        return {"court_id": court_id, "message": "Stub delete – chưa xóa DB"}

    def get_availability(
        self, court_id: int, params: CourtAvailabilityRequest
    ) -> CourtAvailability:
        return CourtAvailability(
            court_id=court_id,
            date=params.date,
            available_slots=["06:00-07:00", "07:00-08:00", "10:00-11:00"],
        )
