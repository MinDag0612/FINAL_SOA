from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from Booking.repository.booking_repository import BookingRepository
from Booking.models.booking_models import (
    BookingCancelRequest,
    BookingCreate,
    BookingRescheduleRequest,
    BookingStatus,
    BookingUpdate,
)


class BookingService:
    def __init__(self, db: Session):
        self.repository = BookingRepository(db)
        self.db = db
    
    def list_bookings(self, user_id: Optional[int] = None, facility_id: Optional[int] = None):
        """List bookings with optional filters"""
        return self.repository.list_bookings(user_id=user_id, facility_id=facility_id)
    
    def create_booking(self, payload: BookingCreate, user_email: str, user_role: str = "customer"):
        """Create a new booking"""
        # Calculate total amount from items
        total_amount = sum(item.price for item in payload.items)
        
        # For first-come-first-served: create with confirmed status and pending payment
        payment_status = "pending"
        status = "confirmed"
        
        return self.repository.create_booking(
            payload=payload,
            total_amount=total_amount,
            payment_status=payment_status,
            status=status,
            user_role=user_role
        )
    
    def get_booking(self, booking_id: int, user_id: Optional[int] = None):
        """Get booking by ID"""
        return self.repository.get_booking(booking_id)

    def reschedule_booking(self, booking_id: int, payload: BookingRescheduleRequest, user_id: Optional[int] = None):
        """Reschedule booking items with new times/prices"""
        return self.repository.reschedule_booking_items(
            booking_id=booking_id,
            updates=payload.items,
            user_id=user_id,
            note=payload.note,
        )
    
    def get_bookings_by_user(self, user_id: int):
        """Get all bookings for a user"""
        return self.repository.list_bookings(user_id=user_id)
    
    def get_bookings_by_facility(self, facility_id: int, date: Optional[str] = None):
        """Get all bookings for a facility, optionally filtered by date"""
        if date:
            # Filter by date using raw SQL
            query = text("""
                SELECT b.booking_id, b.user_id, b.facility_id, b.status, b.total_amount, 
                       b.payment_status, b.payment_method, b.payment_reference, b.paid_at, b.note
                FROM bookings b
                JOIN booking_items bi ON b.booking_id = bi.booking_id
                WHERE b.facility_id = :facility_id 
                AND DATE(bi.start_time) = :date
                GROUP BY b.booking_id
                ORDER BY b.created_at DESC
            """)
            rows = self.db.execute(query, {"facility_id": facility_id, "date": date}).mappings().all()
            items_map = self.repository._fetch_items_map([row["booking_id"] for row in rows])
            return [self.repository._row_to_booking(row, items_map.get(row["booking_id"], [])) for row in rows]
        else:
            return self.repository.list_bookings(facility_id=facility_id)

    def get_booking_logs(self, facility_id: int, date: Optional[str] = None):
        """Get log entries for a facility (used by manager history)"""
        return self.repository.list_logs_by_facility(facility_id, date)

    def log_booking_action(
        self,
        booking_id: int,
        action: str,
        note: Optional[str] = None,
        user_id: Optional[int] = None,
        role: Optional[str] = None,
    ):
        """
        Normalize the parameters expected by the repository-level log helper.
        """
        changed_by_role = role or ("manager" if user_id is None else "staff")
        return self.repository.log_booking_action(
            booking_id=booking_id,
            action_type=action,
            reason=note,
            changed_by_user_id=user_id,
            changed_by_role=changed_by_role,
        )
    
    def get_time_slots_by_court(self, court_id: int):
        """Get time slots for a specific court (for manager timeline)"""
        query = text("""
            SELECT bi.start_time, bi.end_time, b.booking_id, b.status, b.payment_status
            FROM booking_items bi
            JOIN bookings b ON bi.booking_id = b.booking_id
            WHERE bi.court_id = :court_id
            AND b.status != 'cancelled'
            ORDER BY bi.start_time
        """)
        result = self.db.execute(query, {"court_id": court_id}).mappings().all()
        return [dict(row) for row in result]
    
    def update_booking(self, booking_id: int, payload: BookingUpdate, user_id: Optional[int] = None):
        """Update booking"""
        return self.repository.update_booking(booking_id, payload, user_id=user_id)
    
    def cancel_booking(self, booking_id: int, payload: BookingCancelRequest, user_id: Optional[int] = None, user_role: Optional[str] = None):
        """Cancel booking"""
        return self.repository.cancel_booking(booking_id, payload.reason, changed_by=user_id, changed_by_role=user_role or 'customer')
    
    def update_payment_status(
        self, 
        booking_id: int, 
        payment_status: str,
        status: str,
        reference_id: Optional[str] = None,
        paid_at: Optional[datetime] = None
    ):
        """Update payment status"""
        return self.repository.update_payment_status(
            booking_id=booking_id,
            payment_status=payment_status,
            status=BookingStatus(status),
            reference_id=reference_id,
            paid_at=paid_at
        )
    
    def get_all_bookings(self):
        """Get all bookings"""
        return self.repository.list_bookings()
    
    def get_booking_logs_by_id(self, booking_id: int):
        """Get all log entries for a specific booking"""
        return self.repository.get_booking_logs(booking_id)
    
    def get_facility_booking_logs(self, facility_id: int, date: Optional[str] = None, limit: int = 100):
        """Get recent booking logs for a facility"""
        return self.repository.get_facility_booking_logs(facility_id, date, limit)
