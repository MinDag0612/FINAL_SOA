from typing import Dict
from datetime import datetime
import os
import logging
import requests
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ReportService:

    def __init__(self):
        self.booking_service_url = os.getenv(
            "BOOKING_SERVICE_URL", "http://booking_api:8003"
        )

    def get_day_playTime_report(self, court_id: int, token: str) -> Dict[str, float]:
        url = f"{self.booking_service_url}/booking/manager/{court_id}/time_slots"
        total_play_time_per_day: Dict[str, float] = {}
        
        headers = {"Authorization": token}
        try:
            resp = requests.get(url, headers=headers, timeout=5.0)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to get bookings")
            bookings = resp.json()
        except requests.Timeout:
            logger.error(f"Request timeout to {url}")
            raise HTTPException(status_code=504, detail="Booking service timeout")
        except requests.RequestException as e:
            logger.error(f"Failed to reach booking service: {e}")
            raise HTTPException(status_code=502, detail="Failed to reach booking service")
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {}

        # Giả sử bookings["data"] là danh sách booking_items như bạn gửi
        for item in bookings.get("data", []):
            start = datetime.fromisoformat(item["start_time"])
            end = datetime.fromisoformat(item["end_time"])
            
            # Tính số giờ chơi
            hours = (end - start).total_seconds() / 3600

            # Lấy ngày dạng 'YYYY-MM-DD'
            day_str = start.date().isoformat()

            # Cộng dồn số giờ chơi vào cùng ngày
            total_play_time_per_day[day_str] = total_play_time_per_day.get(day_str, 0) + hours

        return total_play_time_per_day
