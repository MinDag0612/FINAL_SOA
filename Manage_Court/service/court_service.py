from datetime import datetime, timedelta
from typing import List, Optional

from models.court_models import (
    AvailabilityRequest,
    Court,
    CourtCreate,
    CourtUpdate,
    MaintenanceCreate,
    MaintenanceEntry,
    Slot,
)
from repository.court_repo import CourtRepo
from repository.maintenance_repo import MaintenanceRepo
from service.facility_client import FacilityClient


class CourtService:
    def __init__(
        self,
        repo: CourtRepo,
        maintenance_repo: MaintenanceRepo,
        facility_client: FacilityClient,
    ):
        self.repo = repo
        self.maintenance_repo = maintenance_repo
        self.facility_client = facility_client

    def list_courts(
        self, facility_id: Optional[int] = None, limit: int = 100, offset: int = 0
    ) -> List[Court]:
        return [
            Court(**item)
            for item in self.repo.list_courts(
                facility_id=facility_id, limit=limit, offset=offset
            )
        ]

    def create_court(self, payload: CourtCreate) -> Court:
        self.facility_client.ensure_exists(payload.facility_id)
        record = self.repo.create_court(payload.model_dump())
        return Court(**record)

    def get_court(self, court_id: int) -> Optional[Court]:
        record = self.repo.get_court(court_id)
        return Court(**record) if record else None

    def update_court(self, court_id: int, payload: CourtUpdate) -> Optional[Court]:
        if payload.facility_id is not None:
            self.facility_client.ensure_exists(payload.facility_id)
        record = self.repo.update_court(court_id, payload.model_dump(exclude_none=True))
        return Court(**record) if record else None

    def delete_court(self, court_id: int) -> bool:
        return self.repo.delete_court(court_id)

    # Maintenance & availability
    def create_maintenance(
        self, court_id: int, payload: MaintenanceCreate
    ) -> MaintenanceEntry:
        record = self.maintenance_repo.create(
            court_id, payload.model_dump(exclude_none=True)
        )
        return MaintenanceEntry(**record)

    def list_maintenance(self, court_id: int, date: str) -> List[MaintenanceEntry]:
        return [
            MaintenanceEntry(**item)
            for item in self.maintenance_repo.list_for_court(court_id, date)
        ]

    def get_availability(
        self, court_id: int, params: AvailabilityRequest
    ) -> List[Slot]:
        blocks = self.maintenance_repo.list_for_court(court_id, params.date)
        unavailable = [(b["start_time"], b["end_time"]) for b in blocks]
        return self._compute_slots(params, unavailable)

    def _compute_slots(
        self, params: AvailabilityRequest, unavailable: List[tuple[str, str]]
    ) -> List[Slot]:
        fmt = "%Y-%m-%d %H:%M"

        def to_dt(t: str) -> datetime:
            return datetime.strptime(f"{params.date} {t}", fmt.replace("%Y-%m-%d ", ""))

        start_dt = to_dt(params.start)
        end_dt = to_dt(params.end)
        step = timedelta(minutes=params.slot_minutes)

        slots: List[Slot] = []
        current = start_dt
        while current + step <= end_dt:
            slot_end = current + step
            slot_str = (current.strftime("%H:%M"), slot_end.strftime("%H:%M"))
            if not self._overlaps(slot_str, unavailable):
                slots.append(Slot(start=slot_str[0], end=slot_str[1]))
            current = slot_end
        return slots

    def _overlaps(self, slot: tuple[str, str], blocks: List[tuple[str, str]]) -> bool:
        s_start = datetime.strptime(slot[0], "%H:%M")
        s_end = datetime.strptime(slot[1], "%H:%M")
        for b_start_str, b_end_str in blocks:
            b_start = datetime.strptime(b_start_str, "%H:%M")
            b_end = datetime.strptime(b_end_str, "%H:%M")
            if s_start < b_end and b_start < s_end:
                return True
        return False
