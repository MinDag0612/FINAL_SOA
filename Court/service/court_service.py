from datetime import datetime, timedelta
from typing import List
from fastapi import HTTPException
<<<<<<< HEAD
=======
import requests
>>>>>>> 7f3ffaacc95ad918698a4d53a6a3079a1216f6d3

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
<<<<<<< HEAD
    def get_courts_by_facility(self, facility_id: int) -> List[Court]:
        try:
=======
    def get_courts_by_facility(self, facility_id: str, user_id: str, token: str):
        url = f"http://facility_api:8005/manager/user_id_by_facility/{facility_id}"
        header = {
            "Authorization": token
        }
        try:
            user_id_court = requests.get(url, headers=header)
            user_id_court = user_id_court.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail="Failed to verify facility manager") from e
        except ValueError:
            print(f"Response is not JSON")
            return None
        user_id_court = user_id_court["user_id"]
    
        try:
            user_id_court_int = int(str(user_id_court).strip())
            user_id_int = int(str(user_id).strip())
            if user_id is None:
                raise HTTPException(status_code=403, detail="Access forbidden: You do not manage this facility. User ID missing")
            
            if int(user_id_court_int) != int(user_id_int):
                raise HTTPException(status_code=403, detail=f"Access forbidden: You do not manage this facility. User ID mismatch. " + str(user_id_court) + " vs " + str(user_id))
            
>>>>>>> 7f3ffaacc95ad918698a4d53a6a3079a1216f6d3
            facility_id = int(facility_id)
            courts = self.court_repo.get_courts_by_facility(facility_id)
            if not courts:
                raise HTTPException(status_code=404, detail="No courts found for this facility")
            return courts
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid facility ID")