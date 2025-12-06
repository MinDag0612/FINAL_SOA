from datetime import datetime
from http.client import HTTPException
from typing import List, Optional
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

from Booking.models.booking_models import (
    Booking,
    BookingCreate,
    BookingItem,
    BookingItemUpdate,
    BookingStatus,
    BookingUpdate,
)


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_bookings(self, user_id: Optional[int] = None, facility_id: Optional[int] = None) -> List[Booking]:
        params = {}
        conditions = []
        if user_id is not None:
            conditions.append("user_id = :user_id")
            params["user_id"] = user_id
        if facility_id is not None:
            conditions.append("facility_id = :facility_id")
            params["facility_id"] = facility_id

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        bookings_query = text(
            f"""
            SELECT booking_id, user_id, facility_id, status, total_amount, payment_status,
                   payment_method, payment_reference, customer_name, customer_phone, customer_email,
                   paid_at, note
            FROM bookings
            {where_clause}
            ORDER BY created_at DESC
            """
        )
        rows = self.db.execute(bookings_query, params).mappings().all()
        items_map = self._fetch_items_map([row["booking_id"] for row in rows])

        return [
            self._row_to_booking(row, items_map.get(row["booking_id"], []))
            for row in rows
        ]

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        row = (
            self.db.execute(
                text(
                    """
                    SELECT booking_id, user_id, facility_id, status, total_amount, payment_status,
                           payment_method, payment_reference, customer_name, customer_phone, customer_email,
                           paid_at, note
                    FROM bookings
                    WHERE booking_id = :booking_id
                    """
                ),
                {"booking_id": booking_id},
            )
            .mappings()
            .first()
        )
        if not row:
            return None

        items = self._fetch_items_map([booking_id]).get(booking_id, [])
        return self._row_to_booking(row, items)

    def create_booking(
        self,
        payload: BookingCreate,
        total_amount: float,
        payment_status: str,
        status: str = "confirmed",  # Default to confirmed (first-come-first-served)
        user_role: str = "customer",
    ) -> Booking:
        result = self.db.execute(
            text(
                """
                INSERT INTO bookings (user_id, facility_id, status, total_amount, payment_status, payment_method, 
                                    customer_name, customer_phone, customer_email, note)
                VALUES (:user_id, :facility_id, :status, :total_amount, :payment_status, :payment_method, 
                        :customer_name, :customer_phone, :customer_email, :note)
                """
            ),
            {
                "user_id": payload.user_id,
                "facility_id": payload.facility_id,
                "status": status,
                "total_amount": total_amount,
                "payment_status": payment_status,
                "payment_method": payload.payment_method,
                "customer_name": payload.customer_name,
                "customer_phone": payload.customer_phone,
                "customer_email": payload.customer_email,
                "note": payload.note,
            },
        )
        booking_id = result.lastrowid

        for item in payload.items:
            self.db.execute(
                text(
                    """
                    INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price)
                    VALUES (:booking_id, :court_id, :start_time, :end_time, :price)
                    """
                ),
                {
                    "booking_id": booking_id,
                    "court_id": item.court_id,
                    "start_time": item.start_time,
                    "end_time": item.end_time,
                    "price": item.price,
                },
            )

        self.db.commit()
        
        # Log booking creation
        self.log_booking_action(
            booking_id=booking_id,
            action_type='created',
            new_status=status,
            new_payment_status=payment_status,
            changed_by_user_id=payload.user_id,
            changed_by_role=user_role,
            reason='New booking created'
        )
        
        return self.get_booking(booking_id)

    def has_conflict_excluding_booking(self, court_id: int, start_time: datetime, end_time: datetime, booking_id: int) -> bool:
        query = text(
            """
            SELECT COUNT(1) as cnt
            FROM booking_items bi
            JOIN bookings b ON bi.booking_id = b.booking_id
            WHERE bi.court_id = :court_id
              AND b.booking_id != :booking_id
              AND (
                  b.status = 'confirmed'
                  OR (b.status = 'pending' AND b.created_at > NOW() - INTERVAL 15 MINUTE)
              )
              AND NOT (bi.end_time <= :start_time OR bi.start_time >= :end_time)
            """
        )
        result = self.db.execute(
            query,
            {
                "court_id": court_id,
                "booking_id": booking_id,
                "start_time": start_time,
                "end_time": end_time,
            },
        ).scalar_one()
        return int(result) > 0

    def log_booking_change(
        self,
        booking_id: int,
        item_id: int,
        court_id: int,
        old_start: datetime,
        old_end: datetime,
        new_start: datetime,
        new_end: datetime,
        old_price: float,
        new_price: float,
        changed_by: Optional[int] = None,
        note: Optional[str] = None,
        action: str = "reschedule",
    ) -> None:
        self.db.execute(
            text(
                """
                INSERT INTO log_booking (
                    booking_id, item_id, court_id,
                    old_start, old_end, new_start, new_end,
                    old_price, new_price, action, changed_by, note
                ) VALUES (
                    :booking_id, :item_id, :court_id,
                    :old_start, :old_end, :new_start, :new_end,
                    :old_price, :new_price, :action, :changed_by, :note
                )
                """
            ),
            {
                "booking_id": booking_id,
                "item_id": item_id,
                "court_id": court_id,
                "old_start": old_start,
                "old_end": old_end,
                "new_start": new_start,
                "new_end": new_end,
                "old_price": old_price,
                "new_price": new_price,
                "action": action,
                "changed_by": changed_by,
                "note": note,
            },
        )

    def reschedule_booking_items(
        self,
        booking_id: int,
        updates: List[BookingItemUpdate],
        user_id: Optional[int] = None,
        note: Optional[str] = None,
    ) -> Booking:
        if not updates:
            raise ValueError("Không có thay đổi nào để cập nhật.")

        for update in updates:
            item_row = (
                self.db.execute(
                    text(
                        """
                        SELECT item_id, court_id, start_time, end_time, price
                        FROM booking_items
                        WHERE item_id = :item_id
                          AND booking_id = :booking_id
                        """
                    ),
                    {"item_id": update.item_id, "booking_id": booking_id},
                )
                .mappings()
                .first()
            )

            if not item_row:
                raise ValueError(f"Không tìm thấy slot với ID {update.item_id}.")

            if update.court_id != item_row["court_id"]:
                raise ValueError("Không thể chuyển slot sang court khác.")

            if update.end_time <= update.start_time:
                raise ValueError("Giờ kết thúc phải lớn hơn giờ bắt đầu.")

            if self.has_conflict_excluding_booking(
                item_row["court_id"],
                update.start_time,
                update.end_time,
                booking_id,
            ):
                raise ValueError("Thời gian đã trùng với booking khác.")

            old_start = item_row["start_time"]
            old_end = item_row["end_time"]
            old_price = float(item_row["price"])

            self.log_booking_change(
                booking_id=booking_id,
                item_id=item_row["item_id"],
                court_id=item_row["court_id"],
                old_start=old_start,
                old_end=old_end,
                new_start=update.start_time,
                new_end=update.end_time,
                old_price=old_price,
                new_price=float(update.price),
                changed_by=user_id,
                note=note,
            )

            self.db.execute(
                text(
                    """
                    UPDATE booking_items
                    SET start_time = :start_time,
                        end_time = :end_time,
                        price = :price
                    WHERE item_id = :item_id
                      AND booking_id = :booking_id
                    """
                ),
                {
                    "start_time": update.start_time,
                    "end_time": update.end_time,
                    "price": update.price,
                    "item_id": update.item_id,
                    "booking_id": booking_id,
                },
            )

        total_amount = self.db.execute(
            text(
                """
                SELECT COALESCE(SUM(price), 0) as total
                FROM booking_items
                WHERE booking_id = :booking_id
                """
            ),
            {"booking_id": booking_id},
        ).scalar_one()

        self.db.execute(
            text(
                """
                UPDATE bookings
                SET total_amount = :total_amount
                WHERE booking_id = :booking_id
                """
            ),
            {
                "total_amount": total_amount,
                "booking_id": booking_id,
            },
        )

        self.db.commit()
        return self.get_booking(booking_id)

    def update_booking(self, booking_id: int, payload: BookingUpdate, user_id: Optional[int] = None) -> Optional[Booking]:
        fields = payload.model_dump(exclude_none=True)
        existing_booking = self.get_booking(booking_id)
        if not fields:
            return self.get_booking(booking_id)

        set_clauses = []
        params = {"booking_id": booking_id}

        if "status" in fields:
            set_clauses.append("status = :status")
            params["status"] = fields["status"]
        if "note" in fields:
            set_clauses.append("note = :note")
            params["note"] = fields["note"]

        if user_id is not None:
            where_clause = "booking_id = :booking_id AND user_id = :user_id"
            params["user_id"] = user_id
        else:
            where_clause = "booking_id = :booking_id"

        query = text(
            f"""
            UPDATE bookings
            SET {", ".join(set_clauses)}
            WHERE {where_clause}
            """
        )
        self.db.execute(query, params)
        self.db.commit()
        new_status = fields.get("status")
        if new_status and existing_booking and existing_booking.status != new_status:
            note = f"{existing_booking.status} → {new_status}"
            self.log_booking_action(
                booking_id=booking_id,
                action_type='status_changed',
                old_status=existing_booking.status,
                new_status=new_status,
                reason=note,
                changed_by_user_id=user_id,
                changed_by_role='manager' if user_id is None else 'staff',
            )
        return self.get_booking(booking_id)

    def update_payment_status(
        self,
        booking_id: int,
        payment_status: str,
        status: BookingStatus,
        reference_id: Optional[str] = None,
        paid_at: Optional[datetime] = None,
        changed_by: Optional[int] = None,
        changed_by_role: Optional[str] = None,
    ) -> Optional[Booking]:
        # Get current booking status before update
        existing = self.get_booking(booking_id)
        old_payment_status = existing.payment_status if existing else None
        old_status = existing.status if existing else None
        
        query = text(
            """
            UPDATE bookings
            SET payment_status = :payment_status,
                status = :status,
                payment_reference = COALESCE(:reference_id, payment_reference),
                paid_at = COALESCE(:paid_at, paid_at)
            WHERE booking_id = :booking_id
            """
        )
        self.db.execute(
            query,
            {
                "payment_status": payment_status,
                "status": status,
                "reference_id": reference_id,
                "paid_at": paid_at,
                "booking_id": booking_id,
            },
        )
        self.db.commit()
        
        # Log payment status change
        self.log_booking_action(
            booking_id=booking_id,
            action_type='payment_updated',
            old_status=old_status,
            new_status=status,
            old_payment_status=old_payment_status,
            new_payment_status=payment_status,
            changed_by_user_id=changed_by,
            changed_by_role=changed_by_role or 'system',
            reason=f'Payment updated: {reference_id}' if reference_id else 'Payment status updated'
        )
        
        return self.get_booking(booking_id)

    def update_payment_reference(self, booking_id: int, reference_id: str) -> None:
        query = text(
            """
            UPDATE bookings
            SET payment_reference = :reference_id
            WHERE booking_id = :booking_id
            """
        )
        self.db.execute(query, {"booking_id": booking_id, "reference_id": reference_id})
        self.db.commit()

    def cancel_booking(self, booking_id: int, reason: Optional[str], changed_by: Optional[int] = None, changed_by_role: Optional[str] = None) -> Optional[Booking]:
        # Get current booking status before update
        existing = self.get_booking(booking_id)
        if not existing:
            return None
        
        old_status = existing.status
        old_payment_status = existing.payment_status
        
        query = text(
            """
            UPDATE bookings
            SET status = 'cancelled',
                payment_status = 'failed',
                cancel_reason = :reason
            WHERE booking_id = :booking_id
            """
        )
        self.db.execute(query, {"booking_id": booking_id, "reason": reason})
        self.db.commit()
        
        # Log cancellation with new booking_logs table
        self.log_booking_action(
            booking_id=booking_id,
            action_type='cancelled',
            old_status=old_status,
            new_status='cancelled',
            old_payment_status=old_payment_status,
            new_payment_status='failed',
            changed_by_user_id=changed_by,
            changed_by_role=changed_by_role or 'system',
            reason=reason or 'Booking cancelled'
        )
        
        return self.get_booking(booking_id)

    def delete_booking(self, booking_id: int) -> bool:
        self.db.execute(
            text(
                """
                DELETE FROM booking_items
                WHERE booking_id = :booking_id
                """
            ),
            {"booking_id": booking_id},
        )
        result = self.db.execute(
            text(
                """
                DELETE FROM bookings
                WHERE booking_id = :booking_id
                """
            ),
            {"booking_id": booking_id},
        )
        self.db.commit()
        return result.rowcount > 0

    def has_conflict(self, court_id: int, start_time: datetime, end_time: datetime) -> bool:
        query = text(
            """
            SELECT COUNT(1) as cnt
            FROM booking_items bi
            JOIN bookings b ON bi.booking_id = b.booking_id
            WHERE bi.court_id = :court_id
              AND (
                  b.status = 'confirmed' 
                  OR (b.status = 'pending' AND b.created_at > NOW() - INTERVAL 15 MINUTE)
              )
              AND NOT (bi.end_time <= :start_time OR bi.start_time >= :end_time)
            """
        )
        result = self.db.execute(
            query,
            {"court_id": court_id, "start_time": start_time, "end_time": end_time},
        ).scalar_one()
        return result > 0

    def has_conflict_excluding(self, court_id: int, start_time: datetime, end_time: datetime, exclude_booking_id: int) -> bool:
        """
        Check for booking conflicts, excluding a specific booking_id.
        Used during payment confirmation to check if slot was taken by another user.
        """
        query = text(
            """
            SELECT COUNT(1) as cnt
            FROM booking_items bi
            JOIN bookings b ON bi.booking_id = b.booking_id
            WHERE bi.court_id = :court_id
              AND b.booking_id != :exclude_booking_id
              AND (
                  b.status = 'confirmed' 
                  OR (b.status = 'pending' AND b.created_at > NOW() - INTERVAL 15 MINUTE)
              )
              AND NOT (bi.end_time <= :start_time OR bi.start_time >= :end_time)
            """
        )
        result = self.db.execute(
            query,
            {
                "court_id": court_id,
                "start_time": start_time,
                "end_time": end_time,
                "exclude_booking_id": exclude_booking_id,
            },
        ).scalar_one()
        return result > 0

    def has_conflict_excluding_user(self, court_id: int, start_time: datetime, end_time: datetime, exclude_user_id: int) -> bool:
        """
        Check for booking conflicts, excluding all bookings from a specific user.
        Used when creating new booking to allow user to replace their own pending bookings.
        """
        query = text(
            """
            SELECT COUNT(1) as cnt
            FROM booking_items bi
            JOIN bookings b ON bi.booking_id = b.booking_id
            WHERE bi.court_id = :court_id
              AND b.user_id != :exclude_user_id
              AND (
                  b.status = 'confirmed' 
                  OR (b.status = 'pending' AND b.created_at > NOW() - INTERVAL 15 MINUTE)
              )
              AND NOT (bi.end_time <= :start_time OR bi.start_time >= :end_time)
            """
        )
        result = self.db.execute(
            query,
            {
                "court_id": court_id,
                "start_time": start_time,
                "end_time": end_time,
                "exclude_user_id": exclude_user_id,
            },
        ).scalar_one()
        return result > 0

    def _fetch_items_map(self, booking_ids: List[int]) -> dict[int, List[BookingItem]]:
        if not booking_ids:
            return {}
        query = (
            text(
                """
                SELECT item_id, booking_id, court_id, start_time, end_time, price
                FROM booking_items
                WHERE booking_id IN :booking_ids
                ORDER BY start_time
                """
            ).bindparams(bindparam("booking_ids", expanding=True))
        )
        rows = self.db.execute(query, {"booking_ids": booking_ids}).mappings().all()
        items_map: dict[int, List[BookingItem]] = {}
        for row in rows:
            item = BookingItem(
                item_id=row["item_id"],
                court_id=row["court_id"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                price=float(row["price"]),
            )
            items_map.setdefault(row["booking_id"], []).append(item)
        return items_map

    def _get_primary_item_for_booking(self, booking_id: int):
        row = self.db.execute(
            text(
                """
                SELECT item_id, court_id, start_time, end_time, price
                FROM booking_items
                WHERE booking_id = :booking_id
                ORDER BY start_time
                LIMIT 1
                """
            ),
            {"booking_id": booking_id},
        ).mappings().first()
        return row

    def _insert_log_entry(
        self,
        booking_id: int,
        item_id: int,
        court_id: int,
        action: str,
        note: Optional[str],
        changed_by: Optional[int],
        start_time,
        end_time,
        price,
    ) -> None:
        self.db.execute(
            text(
                """
                INSERT INTO log_booking (
                    booking_id, item_id, court_id,
                    old_start, old_end, new_start, new_end,
                    old_price, new_price, action, changed_by, note
                ) VALUES (
                    :booking_id, :item_id, :court_id,
                    :old_start, :old_end, :new_start, :new_end,
                    :old_price, :new_price, :action, :changed_by, :note
                )
                """
            ),
            {
                "booking_id": booking_id,
                "item_id": item_id,
                "court_id": court_id,
                "old_start": start_time,
                "old_end": end_time,
                "new_start": start_time,
                "new_end": end_time,
                "old_price": price,
                "new_price": price,
                "action": action,
                "changed_by": changed_by,
                "note": note,
            },
        )

    def log_booking_action(
        self,
        booking_id: int,
        action: str,
        note: Optional[str] = None,
        changed_by: Optional[int] = None,
    ):
        item_row = self._get_primary_item_for_booking(booking_id)
        if not item_row:
            return
        self._insert_log_entry(
            booking_id=booking_id,
            item_id=item_row["item_id"],
            court_id=item_row["court_id"],
            action=action,
            note=note,
            changed_by=changed_by,
            start_time=item_row["start_time"],
            end_time=item_row["end_time"],
            price=float(item_row["price"]),
        )

    def list_logs_by_facility(self, facility_id: int, date: Optional[str] = None) -> List[dict]:
        params = {"facility_id": facility_id}
        date_clause = ""
        if date:
            date_clause = "AND DATE(bi.start_time) = :date"
            params["date"] = date

        query = text(
            f"""
            SELECT
                lb.log_id,
                lb.booking_id,
                lb.action,
                lb.note,
                lb.changed_by,
                lb.created_at,
                bi.start_time,
                bi.end_time,
                bi.court_id
            FROM log_booking lb
            JOIN booking_items bi ON lb.item_id = bi.item_id
            JOIN bookings b ON lb.booking_id = b.booking_id
            WHERE b.facility_id = :facility_id
            {date_clause}
            ORDER BY lb.created_at DESC
            """
        )

        rows = self.db.execute(query, params).mappings().all()
        return [dict(row) for row in rows]

    def _row_to_booking(self, row, items: List[BookingItem]) -> Booking:
        return Booking(
            booking_id=row["booking_id"],
            user_id=row["user_id"],
            facility_id=row["facility_id"],
            status=row["status"],  # type: ignore[arg-type]
            total_amount=float(row["total_amount"]),
            payment_status=row.get("payment_status"),
            payment_method=row.get("payment_method"),
            payment_reference=row.get("payment_reference"),
            customer_name=row.get("customer_name"),
            customer_phone=row.get("customer_phone"),
            customer_email=row.get("customer_email"),
            paid_at=row.get("paid_at"),
            items=items,
        )
        
#--------- FOR MANAGER FLOW --------------
    def get_time_slots_by_court(self, court_id: int) -> List[dict]:
        try:
            query = text(
                """
                SELECT bi.item_id, bi.booking_id, bi.court_id, bi.start_time, bi.end_time, bi.price, b.payment_status
                FROM booking_items bi
                JOIN bookings b ON bi.booking_id = b.booking_id
                WHERE bi.court_id = :court_id
                  AND b.payment_status = 'paid'
                ORDER BY bi.start_time
                """
            )
            rows = self.db.execute(query, {"court_id": court_id}).mappings().all()
            slots = [
                {
                    "item_id": row["item_id"],
                    "booking_id": row["booking_id"],
                    "court_id": row["court_id"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "price": float(row["price"]),
                    "payment_status": row["payment_status"],
                }
                for row in rows
            ]
            return slots
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def search_by_timeslot(self, date: str, start_time: str, end_time: str, facility_id: Optional[int] = None) -> dict:
        """Search bookings within a specific timeslot"""
        try:
            # Combine date and time for comparison
            start_datetime = f"{date} {start_time}"
            end_datetime = f"{date} {end_time}"
            
            conditions = [
                "bi.start_time < :end_datetime",
                "bi.end_time > :start_datetime"
            ]
            params = {
                "start_datetime": start_datetime,
                "end_datetime": end_datetime
            }
            
            if facility_id is not None:
                conditions.append("b.facility_id = :facility_id")
                params["facility_id"] = facility_id
            
            where_clause = " AND ".join(conditions)
            
            query = text(
                f"""
                SELECT 
                    COUNT(DISTINCT b.booking_id) as total_bookings,
                    COUNT(DISTINCT bi.item_id) as total_slots,
                    bi.court_id,
                    COUNT(bi.court_id) as court_booking_count
                FROM bookings b
                INNER JOIN booking_items bi ON b.booking_id = bi.booking_id
                WHERE {where_clause}
                GROUP BY bi.court_id
                """
            )
            
            rows = self.db.execute(query, params).mappings().all()
            
            courts_breakdown = [
                {
                    "court_id": row["court_id"],
                    "booking_count": row["court_booking_count"]
                }
                for row in rows
            ]
            
            total_bookings = sum(row["court_booking_count"] for row in rows)
            
            return {
                "total_bookings": total_bookings,
                "total_players": total_bookings,  # Assuming 1 booking = 1 player (can be adjusted)
                "courts_breakdown": courts_breakdown
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def log_booking_action(
        self,
        booking_id: int,
        action_type: str,
        old_status: Optional[str] = None,
        new_status: Optional[str] = None,
        old_payment_status: Optional[str] = None,
        new_payment_status: Optional[str] = None,
        changed_by_user_id: Optional[int] = None,
        changed_by_role: Optional[str] = None,
        reason: Optional[str] = None,
        changes_json: Optional[str] = None,
    ) -> None:
        """
        Insert a log entry into booking_logs table to track all booking actions.
        
        Args:
            booking_id: ID of the booking
            action_type: 'created', 'updated', 'cancelled', 'status_changed', 'payment_updated'
            old_status: Previous booking status (if changed)
            new_status: New booking status (if changed)
            old_payment_status: Previous payment status (if changed)
            new_payment_status: New payment status (if changed)
            changed_by_user_id: ID of user who made the change
            changed_by_role: Role of user ('customer', 'manager', 'staff', 'system')
            reason: Optional reason for the change
            changes_json: Optional JSON string with detailed changes
        """
        try:
            self.db.execute(
                text(
                    """
                    INSERT INTO booking_logs (
                        booking_id, action_type,
                        old_status, new_status,
                        old_payment_status, new_payment_status,
                        changed_by_user_id, changed_by_role,
                        reason, changes_json
                    ) VALUES (
                        :booking_id, :action_type,
                        :old_status, :new_status,
                        :old_payment_status, :new_payment_status,
                        :changed_by_user_id, :changed_by_role,
                        :reason, :changes_json
                    )
                    """
                ),
                {
                    "booking_id": booking_id,
                    "action_type": action_type,
                    "old_status": old_status,
                    "new_status": new_status,
                    "old_payment_status": old_payment_status,
                    "new_payment_status": new_payment_status,
                    "changed_by_user_id": changed_by_user_id,
                    "changed_by_role": changed_by_role,
                    "reason": reason,
                    "changes_json": changes_json,
                },
            )
            self.db.commit()
        except Exception as e:
            print(f"[log_booking_action] Error logging action: {e}")
            # Don't raise - logging should not break the main flow

    def get_booking_logs(self, booking_id: int) -> List[dict]:
        """Retrieve all log entries for a specific booking, ordered by time."""
        rows = self.db.execute(
            text(
                """
                SELECT log_id, booking_id, action_type,
                       old_status, new_status,
                       old_payment_status, new_payment_status,
                       changed_by_user_id, changed_by_role,
                       reason, changes_json, created_at
                FROM booking_logs
                WHERE booking_id = :booking_id
                ORDER BY created_at ASC
                """
            ),
            {"booking_id": booking_id},
        ).mappings().all()
        
        return [dict(row) for row in rows]

    def get_facility_booking_logs(
        self, 
        facility_id: int, 
        date: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """Retrieve recent booking logs for a facility, optionally filtered by date of booking (not log creation)."""
        params = {"facility_id": facility_id, "limit": limit}
        conditions = ["b.facility_id = :facility_id"]
        
        if date:
            # Filter by booking date (from booking_items) instead of log created_at
            conditions.append("EXISTS (SELECT 1 FROM booking_items bi WHERE bi.booking_id = b.booking_id AND DATE(bi.start_time) = :date)")
            params["date"] = date
        
        where_clause = " AND ".join(conditions)
        
        rows = self.db.execute(
            text(
                f"""
                SELECT bl.log_id, bl.booking_id, bl.action_type,
                       bl.old_status, bl.new_status,
                       bl.old_payment_status, bl.new_payment_status,
                       bl.changed_by_user_id, bl.changed_by_role,
                       bl.reason, bl.changes_json, bl.created_at,
                       b.customer_name, b.customer_phone
                FROM booking_logs bl
                INNER JOIN bookings b ON bl.booking_id = b.booking_id
                WHERE {where_clause}
                ORDER BY bl.log_id DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()
        
        return [dict(row) for row in rows]
