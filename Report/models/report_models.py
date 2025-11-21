from pydantic import BaseModel


class RevenueQuery(BaseModel):
    date_from: str
    date_to: str


class UsageQuery(BaseModel):
    facility_id: int
    date_from: str
    date_to: str


class CancellationQuery(BaseModel):
    date_from: str
    date_to: str


class DailySummaryQuery(BaseModel):
    date: str


class RevenueReport(BaseModel):
    total_revenue: float
    total_bookings: int
    currency: str = "VND"


class UsageReport(BaseModel):
    facility_id: int
    utilization_rate: float
    total_hours: int


class CancellationReport(BaseModel):
    cancelled: int
    confirmed: int
    cancellation_rate: float


class DailySummary(BaseModel):
    date: str
    revenue: float
    bookings: int
