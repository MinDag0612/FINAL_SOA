from datetime import datetime
from http.client import HTTPException
from typing import List, Optional
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

from Booking.models.booking_models import Booking, BookingCreate, BookingItem, BookingStatus, BookingUpdate


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
                   payment_method, payment_reference, paid_at, note
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
                           payment_method, payment_reference, paid_at, note
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
    ) -> Booking:
        result = self.db.execute(
            text(
                """
                INSERT INTO bookings (user_id, facility_id, status, total_amount, payment_status, payment_method, note)
                VALUES (:user_id, :facility_id, 'pending', :total_amount, :payment_status, :payment_method, :note)
                """
            ),
            {
                "user_id": payload.user_id,
                "facility_id": payload.facility_id,
                "total_amount": total_amount,
                "payment_status": payment_status,
                "payment_method": payload.payment_method,
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
        return self.get_booking(booking_id)

    def update_booking(self, booking_id: int, payload: BookingUpdate) -> Optional[Booking]:
        fields = payload.model_dump(exclude_none=True)
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

        query = text(
            f"""
            UPDATE bookings
            SET {", ".join(set_clauses)}
            WHERE booking_id = :booking_id
            """
        )
        self.db.execute(query, params)
        self.db.commit()
        return self.get_booking(booking_id)

    def update_payment_status(
        self,
        booking_id: int,
        payment_status: str,
        status: BookingStatus,
        reference_id: Optional[str] = None,
        paid_at: Optional[datetime] = None,
    ) -> Optional[Booking]:
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

    def cancel_booking(self, booking_id: int, reason: Optional[str]) -> Optional[Booking]:
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
              AND b.status IN ('pending', 'confirmed')
              AND NOT (bi.end_time <= :start_time OR bi.start_time >= :end_time)
            """
        )
        result = self.db.execute(
            query,
            {"court_id": court_id, "start_time": start_time, "end_time": end_time},
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
                court_id=row["court_id"],
                start_time=row["start_time"],
                end_time=row["end_time"],
                price=float(row["price"]),
            )
            items_map.setdefault(row["booking_id"], []).append(item)
        return items_map

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
