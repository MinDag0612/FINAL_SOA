from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session


class MaintenanceRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_for_court(self, court_id: int, date: str) -> List[dict]:
        result = self.db.execute(
            text(
                """
                SELECT maintenance_id, court_id, date, start_time, end_time, reason, status
                FROM CourtMaintenance
                WHERE court_id = :court_id AND date = :date
                ORDER BY start_time
                """
            ),
            {"court_id": court_id, "date": date},
        )
        return [dict(row._mapping) for row in result]

    def create(self, court_id: int, payload: dict) -> dict:
        params = payload | {"court_id": court_id}
        result = self.db.execute(
            text(
                """
                INSERT INTO CourtMaintenance (court_id, date, start_time, end_time, reason, status)
                VALUES (:court_id, :date, :start_time, :end_time, :reason, :status)
                """
            ),
            params,
        )
        self.db.commit()
        new_id = result.lastrowid
        return self.get(court_id, new_id)

    def get(self, court_id: int, maintenance_id: int) -> dict | None:
        row = (
            self.db.execute(
                text(
                    """
                    SELECT maintenance_id, court_id, date, start_time, end_time, reason, status
                    FROM CourtMaintenance
                    WHERE maintenance_id = :maintenance_id AND court_id = :court_id
                    """
                ),
                {"maintenance_id": maintenance_id, "court_id": court_id},
            )
            .mappings()
            .first()
        )
        return dict(row) if row else None
