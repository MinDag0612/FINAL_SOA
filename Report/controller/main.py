from typing import Dict
from fastapi import Depends, FastAPI, HTTPException, Header

from Report.models.report_models import (
    CancellationQuery,
    DailySummaryQuery,
    RevenueQuery,
    UsageQuery,
)
from Report.service.report_service import ReportService
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse
from jwt_shared.dependencies import get_current_user

app = FastAPI()


def get_service() -> ReportService:
    return ReportService()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "report"}


def check_staff_court_access(user: dict, court_id: int) -> bool:
    """Check if staff has access to a specific court"""
    import httpx
    role = user.get("infor", {}).get("role")
    
    if role == "manager":
        return True  # Manager has full access
    elif role == "staff":
        try:
            user_id = int(user.get("sub"))
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(
                    f"http://court_service:8004/staff/courts",
                    headers={"Authorization": f"Bearer {user_id}"}
                )
                if resp.status_code == 200:
                    courts = resp.json().get("data", [])
                    return any(c["court_id"] == court_id for c in courts)
        except Exception:
            pass
    return False


@app.get("/report/manager/report-playtime-plot/court={court_id}")
def get_plot(
    court_id: int,
    service: "ReportService" = Depends(get_service),
    token: str = Header(None, alias="Authorization"),
    user: dict = Depends(get_current_user),
):
    """Get playtime report for a specific court - Staff can only see today's data"""
    role = user.get("infor", {}).get("role")
    
    # Check role permissions
    if role not in ["manager", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: managers and staff only"
        )
    
    # Check court access for staff
    if role == "staff" and not check_staff_court_access(user, court_id):
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: You don't have permission to view this court"
        )
    
    try:
        # Lấy dữ liệu: dict {day: total_hours}
        playtime_per_day: Dict[str, float] = service.get_day_playTime_report(court_id, token)
        
        # For STAFF: Filter to show only today's data
        if role == "staff":
            from datetime import date
            today = date.today().isoformat()
            playtime_per_day = {k: v for k, v in playtime_per_day.items() if k == today}
        
        if not playtime_per_day:
            raise HTTPException(status_code=404, detail="No playtime data found")
        
        # ----- Vẽ biểu đồ -----
        fig, ax = plt.subplots(figsize=(8, 8))
        days = list(playtime_per_day.keys())
        hours = list(playtime_per_day.values())

        ax.bar(days, hours, color="skyblue")
        ax.set_title(f"Total Playtime per Day for Court {court_id}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Hours")
        ax.set_xticklabels(days, rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # ----- Lưu ảnh vào buffer -----
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        return StreamingResponse(buf, media_type="image/png")
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)