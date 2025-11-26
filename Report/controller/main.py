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
from jwt_shared.jwt import jwt_services

app = FastAPI()


def get_service() -> ReportService:
    return ReportService()

jwt_services = jwt_services()


def get_current_user(token: str = Depends(jwt_services.oauth2_scheme)):
    try:
        payload = jwt_services.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "report"}


@app.get("/manager/report-playtime-plot/court={court_id}")
def get_plot(
    court_id: int,
    service: "ReportService" = Depends(get_service),
    token: str = Header(None, alias="Authorization")
):
    try:
        # Lấy dữ liệu: dict {day: total_hours}
        playtime_per_day: Dict[str, float] = service.get_day_playTime_report(court_id, token)
        
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