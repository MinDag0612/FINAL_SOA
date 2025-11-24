import os
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
from fastapi import HTTPException

from Booking.message import send_event
from Booking.models.booking_models import (
    Booking,
    BookingCancelRequest,
    BookingCreate,
    BookingItem,
    BookingUpdate,
    PaymentStatusUpdate,
)
from Booking.repository.booking_repository import BookingRepository


class BookingService:
    """Booking flow with DB + external billing and court checks."""

    def __init__(self, db_session):
        self.repo = BookingRepository(db_session)
        self.court_service_url = os.getenv("COURT_SERVICE_URL", "http://court_api:8004")
        self.facility_service_url = os.getenv("FACILITY_SERVICE_URL", "http://facility_api:8005")
        self.billing_service_url = os.getenv("BILLING_SERVICE_URL", "http://billing_api:8002")
        self.hold_minutes = int(os.getenv("BOOKING_HOLD_MINUTES", "15"))

    def list_bookings(self, user_id: Optional[int] = None) -> List[Booking]:
        self.repo.cleanup_expired_holds()
        return self.repo.list_bookings(user_id=user_id)

    def get_booking(self, booking_id: int, user_id: Optional[int] = None) -> Booking:
        self.repo.cleanup_expired_holds()
        booking = self.repo.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if user_id and booking.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return booking

    def create_booking(self, payload: BookingCreate) -> dict:
        self.repo.cleanup_expired_holds()
        if payload.user_id is None:
            raise HTTPException(status_code=400, detail="Missing user_id for booking")
        self._validate_items(payload.items)
        self._verify_facility_and_courts(payload.facility_id, [i.court_id for i in payload.items])
        self._ensure_slots_available(payload.items)

        hold_expires_at = datetime.utcnow() + timedelta(minutes=self.hold_minutes)
        total_amount = self._calculate_total(payload.items)

        booking = self.repo.create_booking(
            payload=payload,
            total_amount=total_amount,
            hold_expires_at=hold_expires_at,
            payment_status="pending",
        )

        invoice = None
        payment_intent = None
        billing_error = None
        try:
            invoice = self._create_invoice(booking)
            invoice_data = invoice.get("data") if isinstance(invoice, dict) else None
            invoice_id = None
            if isinstance(invoice_data, dict):
                invoice_id = invoice_data.get("invoice_id") or invoice_data.get("id")
            if invoice_id:
                self.repo.update_payment_reference(booking.booking_id, str(invoice_id))
                booking.payment_reference = str(invoice_id)
                payment_intent = self._initiate_payment(invoice_id, booking, payload.payment_method)
        except Exception as exc:
            billing_error = str(exc)

        return {
            "booking": booking,
            "invoice": invoice,
            "payment_intent": payment_intent,
            "billing_error": billing_error,
        }

    def update_booking(self, booking_id: int, payload: BookingUpdate, user_id: Optional[int] = None) -> Booking:
        booking = self.get_booking(booking_id, user_id)
        if booking.status not in ("pending", "confirmed"):
            raise HTTPException(status_code=400, detail="Cannot update booking in current status")
        updated = self.repo.update_booking(booking_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Booking not found")
        return updated

    def cancel_booking(self, booking_id: int, payload: BookingCancelRequest, user_id: Optional[int] = None) -> Booking:
        booking = self.get_booking(booking_id, user_id)
        if booking.status in ("cancelled", "completed"):
            return booking
        cancelled = self.repo.cancel_booking(booking_id, payload.reason)
        if not cancelled:
            raise HTTPException(status_code=404, detail="Booking not found")
        return cancelled

    def update_payment_status(self, booking_id: int, payload: PaymentStatusUpdate) -> Booking:
        booking = self.repo.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if payload.status == "paid":
            updated = self.repo.update_payment_status(
                booking_id,
                payment_status="paid",
                status="confirmed",
                reference_id=payload.reference_id,
                paid_at=datetime.utcnow(),
            )
            if updated:
                self._emit_booking_confirmed(updated)
        else:
            updated = self.repo.update_payment_status(
                booking_id,
                payment_status="failed",
                status="cancelled",
                reference_id=payload.reference_id,
                paid_at=None,
            )
        if not updated:
            raise HTTPException(status_code=404, detail="Booking not found")
        return updated

    # -------- Internal helpers --------
    def _validate_items(self, items: List[BookingItem]) -> None:
        if not items:
            raise HTTPException(status_code=400, detail="Booking items cannot be empty")
        for item in items:
            if item.start_time >= item.end_time:
                raise HTTPException(status_code=400, detail="start_time must be before end_time")

    def _ensure_slots_available(self, items: List[BookingItem]) -> None:
        for item in items:
            if self.repo.has_conflict(item.court_id, item.start_time, item.end_time):
                raise HTTPException(
                    status_code=409,
                    detail=f"Court {item.court_id} is not available for the requested slot",
                )

    def _calculate_total(self, items: List[BookingItem]) -> float:
        return float(sum(item.price for item in items))

    def _verify_facility_and_courts(self, facility_id: int, court_ids: List[int]) -> None:
        try:
            with httpx.Client(timeout=5.0) as client:
                facility_resp = client.get(f"{self.facility_service_url}/facility/{facility_id}")
                if facility_resp.status_code != 200:
                    raise HTTPException(status_code=404, detail="Facility not found")

                for court_id in set(court_ids):
                    resp = client.get(f"{self.court_service_url}/court/{court_id}")
                    if resp.status_code != 200:
                        raise HTTPException(status_code=404, detail=f"Court {court_id} not found")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Cannot reach court service: {exc}")

    def _create_invoice(self, booking: Booking) -> dict:
        payload = {
            "booking_id": booking.booking_id,
            "user_id": booking.user_id,
            "amount": booking.total_amount,
            "currency": "VND",
            "description": f"Booking #{booking.booking_id}",
        }
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(f"{self.billing_service_url}/billing", json=payload)
            resp.raise_for_status()
            return resp.json()

    def _initiate_payment(self, invoice_id: int, booking: Booking, method: str) -> Optional[dict]:
        payload = {"method": method, "booking_id": booking.booking_id}
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(f"{self.billing_service_url}/billing/{invoice_id}/pay", json=payload)
            resp.raise_for_status()
            return resp.json()

    def _emit_booking_confirmed(self, booking: Booking) -> None:
        try:
            event_payload = {
                "booking_id": booking.booking_id,
                "user_id": booking.user_id,
                "facility_id": booking.facility_id,
                "status": booking.status,
                "items": [
                    {
                        "court_id": item.court_id,
                        "start_time": item.start_time.isoformat(),
                        "end_time": item.end_time.isoformat(),
                    }
                    for item in booking.items
                ],
            }
            send_event("BOOKING_CONFIRMED", event_payload)
        except Exception:
            # Swallow errors so payment callback does not fail
            pass
