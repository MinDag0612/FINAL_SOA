from datetime import datetime, timedelta
from typing import List
from fastapi import HTTPException

from Court.models.court_models import (
    Court,
    CourtAvailability,
    CourtAvailabilityRequest,
    CourtCreate,
    CourtUpdate,
)
from Court.repository.court_repository import CourtRepository


class CourtService:
    """Business logic for court CRUD and availability."""

    def __init__(self, court_repo: CourtRepository):
        self.court_repo = court_repo

    def list_courts(self) -> List[Court]:
        return self.court_repo.list_courts()

    def create_court(self, payload: CourtCreate) -> Court:
        return self.court_repo.create_court(payload)

    def get_court(self, court_id: int) -> Court:
        court = self.court_repo.get_court(court_id)
        if not court:
            raise HTTPException(status_code=404, detail="Court not found")
        return court

    def update_court(self, court_id: int, payload: CourtUpdate) -> Court:
        court = self.court_repo.update_court(court_id, payload)
        if not court:
            raise HTTPException(status_code=404, detail="Court not found")
        return court

    def delete_court(self, court_id: int) -> dict:
        deleted = self.court_repo.delete_court(court_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Court not found")
        return {"court_id": court_id, "message": "Court deactivated"}

    def get_availability(
        self, court_id: int, params: CourtAvailabilityRequest
    ) -> CourtAvailability:
        court = self.court_repo.get_court(court_id)
        if not court:
            raise HTTPException(status_code=404, detail="Court not found")

        slots: List[str] = []
        hours = court.available_hours or [f"{hour:02d}:00" for hour in range(0, 24)]
        for start in hours:
            try:
                start_dt = datetime.strptime(start, "%H:%M")
            except ValueError:
                continue
            end_dt = start_dt + timedelta(hours=1)
            slots.append(f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}")

        return CourtAvailability(
            court_id=court_id,
            date=params.date,
            available_slots=slots,
        )
#------------------FOR MANAGER FLOW----------------------------------
    def get_courts_by_facility(self, facility_id: int) -> List[Court]:
        try:
            courts = self.court_repo.get_courts_by_facility(facility_id)
            if not courts:
                raise HTTPException(status_code=404, detail="No courts found for this facility")
            return courts
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid facility ID")

#------------------FOR STAFF FLOW----------------------------------
    def get_staff_courts(self, staff_id: int) -> List[Court]:
        """Get all courts assigned to a staff member"""
        courts = self.court_repo.get_staff_assigned_courts(staff_id)
        return courts
    
    def check_staff_can_access_court(self, staff_id: int, court_id: int) -> bool:
        """Verify if staff has access to a specific court"""
        return self.court_repo.check_staff_has_court_access(staff_id, court_id)

#------------------PRICE HISTORY----------------------------------
    def get_price_history(self, court_id: int) -> dict:
        """Get price change history and current price schedules for a court"""
        court = self.court_repo.get_court(court_id)
        if not court:
            raise HTTPException(status_code=404, detail="Court not found")
        
        history = self.court_repo.get_court_price_history(court_id)
        schedules = self.court_repo.get_price_schedules(court_id)
        
        return {
            "court_id": court_id,
            "court_name": court.name,
            "current_hourly_rate": court.hourly_rate,
            "price_history": history,
            "price_schedules": schedules
        }
