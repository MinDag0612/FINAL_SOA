from models.report_models import (
    CancellationQuery,
    CancellationReport,
    DailySummary,
    DailySummaryQuery,
    RevenueQuery,
    RevenueReport,
    UsageQuery,
    UsageReport,
)


class ReportService:
    """Stub report service trả dữ liệu thống kê giả lập."""

    def get_revenue(self, params: RevenueQuery) -> RevenueReport:
        return RevenueReport(
            total_revenue=15000000,
            total_bookings=120,
            currency="VND",
        )

    def get_usage(self, params: UsageQuery) -> UsageReport:
        return UsageReport(
            facility_id=params.facility_id,
            utilization_rate=0.82,
            total_hours=320,
        )

    def get_cancellation(self, params: CancellationQuery) -> CancellationReport:
        return CancellationReport(
            cancelled=5,
            confirmed=95,
            cancellation_rate=0.05,
        )

    def get_daily_summary(self, params: DailySummaryQuery) -> DailySummary:
        return DailySummary(
            date=params.date,
            revenue=5000000,
            bookings=40,
        )
