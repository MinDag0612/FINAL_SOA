from fastapi import Depends, FastAPI

from models.report_models import (
    CancellationQuery,
    DailySummaryQuery,
    RevenueQuery,
    UsageQuery,
)
from service.report_service import ReportService

app = FastAPI()


def get_service() -> ReportService:
    return ReportService()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "report"}


@app.get("/report/revenue")
def revenue_report(
    params: RevenueQuery = Depends(), service: ReportService = Depends(get_service)
):
    return {"status": "success", "data": service.get_revenue(params)}


@app.get("/report/usage")
def usage_report(
    params: UsageQuery = Depends(), service: ReportService = Depends(get_service)
):
    return {"status": "success", "data": service.get_usage(params)}


@app.get("/report/cancellation")
def cancellation_report(
    params: CancellationQuery = Depends(),
    service: ReportService = Depends(get_service),
):
    return {"status": "success", "data": service.get_cancellation(params)}


@app.get("/report/daily-summary")
def daily_summary(
    params: DailySummaryQuery = Depends(),
    service: ReportService = Depends(get_service),
):
    return {"status": "success", "data": service.get_daily_summary(params)}
