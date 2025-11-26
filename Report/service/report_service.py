from typing import Dict
from datetime import datetime
import requests
from fastapi import HTTPException

class ReportService:
    """Stub report service trả dữ liệu thống kê."""

    def get_day_playTime_report(self, court_id: int, token: str) -> Dict[str, float]:
        """
        Trả về tổng số giờ chơi mỗi ngày cho court_id.
        Output: { "YYYY-MM-DD": total_hours }
        """
        url = f"http://booking_api:8003/manager/court_id={court_id}/time_slots"
        total_play_time_per_day: Dict[str, float] = {}
        
        headers = {"Authorization": token}
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to get bookings")
            bookings = resp.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail="Failed to verify facility manager") from e
        except ValueError:
            print("Response is not JSON")
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
