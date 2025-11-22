from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class CourtRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_courts(self) -> List[dict]:
        result = self.db.execute(
            text(
                """
                SELECT court_id, facility_id, court_name, price_per_hour, description
                FROM Court
                ORDER BY court_id
                """
            )
        )
        return [dict(row._mapping) for row in result]

    def get_court(self, court_id: int) -> Optional[dict]:
        row = (
            self.db.execute(
                text(
                    """
                    SELECT court_id, facility_id, court_name, price_per_hour, description
                    FROM Court
                    WHERE court_id = :court_id
                    """
                ),
                {"court_id": court_id},
            )
            .mappings()
            .first()
        )
        return dict(row) if row else None

    def create_court(self, payload: dict) -> dict:
        result = self.db.execute(
            text(
                """
                INSERT INTO Court (facility_id, court_name, price_per_hour, description)
                VALUES (:facility_id, :court_name, :price_per_hour, :description)
                """
            ),
            payload,
        )
        self.db.commit()
        new_id = result.lastrowid
        return self.get_court(new_id)

    def update_court(self, court_id: int, fields: dict) -> Optional[dict]:
        if not fields:
            return self.get_court(court_id)

        set_clause = ", ".join([f"{key} = :{key}" for key in fields.keys()])
        params = fields | {"court_id": court_id}
        result = self.db.execute(
            text(f"UPDATE Court SET {set_clause} WHERE court_id = :court_id"),
            params,
        )
        self.db.commit()
        if result.rowcount == 0:
            return None
        return self.get_court(court_id)

    def delete_court(self, court_id: int) -> bool:
        result = self.db.execute(
            text("DELETE FROM Court WHERE court_id = :court_id"),
            {"court_id": court_id},
        )
        self.db.commit()
        return result.rowcount > 0
