from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CourtPriceHistoryItem(BaseModel):
    log_id: int
    court_id: int
    old_hourly_rate: Optional[float]
    new_hourly_rate: float
    changed_at: datetime
    status: str  # 'official' or 'discarded'


class PriceSchedule(BaseModel):
    price_id: int
    court_id: int
    price: float
    days: List[str]  # ["Mon", "Tue", ...]
    hours_start: str  # "06:00"
    hours_end: str  # "17:00"
    status: str  # 'official' or 'discarded'
