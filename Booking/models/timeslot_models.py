from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TimeslotSearchRequest(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    facility_id: Optional[int] = None


class TimeslotSearchResult(BaseModel):
    date: str
    start_time: str
    end_time: str
    total_bookings: int
    total_players: int
    courts_breakdown: list  # [{court_id, court_name, booking_count}]
