from typing import List
from models.facility_models import Facility, FacilityCreate, FacilityUpdate


class FacilityService:
    """Stub service cho Facility: trả dữ liệu mẫu, chưa truy DB."""

    def __init__(self):
        self._sample = Facility(
            facility_id=1,
            name="Badminton Center A",
            address="123 Nguyễn Văn Cừ, Q5, TP.HCM",
            description="Cơ sở tiêu chuẩn với 6 sân và phòng thay đồ.",
            opening_hours="06:00-23:00",
            contact_phone="0123 456 789",
            amenities=["Bãi giữ xe", "KS tự động", "Shop dụng cụ"],
            is_active=True,
        )

    def list_facilities(self) -> List[Facility]:
        return [self._sample]

    def create_facility(self, payload: FacilityCreate) -> Facility:
        return Facility(
            facility_id=99,
            name=payload.name,
            address=payload.address,
            description=payload.description,
            opening_hours=payload.opening_hours,
            contact_phone=payload.contact_phone,
            amenities=payload.amenities,
            is_active=True,
        )

    def get_facility(self, facility_id: int) -> Facility:
        return self._sample.copy(update={"facility_id": facility_id})

    def update_facility(self, facility_id: int, payload: FacilityUpdate) -> dict:
        return {
            "facility_id": facility_id,
            "updated_fields": payload.model_dump(exclude_none=True),
            "message": "Stub update – chưa lưu DB",
        }

    def delete_facility(self, facility_id: int) -> dict:
        return {"facility_id": facility_id, "message": "Stub delete – chưa xóa DB"}
