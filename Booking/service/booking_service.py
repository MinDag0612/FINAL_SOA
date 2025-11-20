from typing import List
from models.booking_models import (
    Booking,
    BookingCancelRequest,
    BookingCreate,
    BookingItem,
    BookingUpdate,
    PaymentStatusUpdate,
)


class BookingService:
    """Stub booking service."""

    def __init__(self):
        sample_item = BookingItem(
            court_id=1, start_time="2024-06-20T08:00", end_time="2024-06-20T09:00", price=150000
        )
        self._sample = Booking(
            booking_id=1,
            status="confirmed",
            total_amount=150000,
            user_id=9,
            facility_id=1,
            items=[sample_item],
        )

    def list_bookings(self) -> List[Booking]:
        return [self._sample]

    def create_booking(self, payload: BookingCreate) -> Booking:
        total = sum(item.price for item in payload.items)
        return Booking(
            booking_id=88,
            status="pending",
            total_amount=total,
            user_id=payload.user_id,
            facility_id=payload.facility_id,
            items=payload.items,
        )

    def get_booking(self, booking_id: int) -> Booking:
        return self._sample.copy(update={"booking_id": booking_id})

    def update_booking(self, booking_id: int, payload: BookingUpdate) -> dict:
        return {
            "booking_id": booking_id,
            "updated_fields": payload.model_dump(exclude_none=True),
            "message": "Stub update – chưa lưu DB",
        }

    def cancel_booking(self, booking_id: int, payload: BookingCancelRequest) -> dict:
        return {
            "booking_id": booking_id,
            "status": "cancelled",
            "reason": payload.reason,
            "message": "Stub cancel – chưa cập nhật DB",
        }

    def update_payment_status(
        self, booking_id: int, payload: PaymentStatusUpdate
    ) -> dict:
        return {
            "booking_id": booking_id,
            "payment_status": payload.status,
            "reference_id": payload.reference_id,
            "message": "Stub payment callback – chưa đồng bộ thực tế",
        }
