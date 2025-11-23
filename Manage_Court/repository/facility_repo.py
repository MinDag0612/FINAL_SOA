from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class FacilityRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_facilities(self) -> List[dict]:
        result = self.db.execute(
            text(
                """
                SELECT facility_id, user_id, facility_name, location, sport, description
                FROM Facility
                ORDER BY facility_id
                """
            )
        )
        return [dict(row._mapping) for row in result]

    def get_facility(self, facility_id: int) -> Optional[dict]:
        row = (
            self.db.execute(
                text(
                    """
                    SELECT facility_id, user_id, facility_name, location, sport, description
                    FROM Facility
                    WHERE facility_id = :facility_id
                    """
                ),
                {"facility_id": facility_id},
            )
            .mappings()
            .first()
        )
        return dict(row) if row else None

    def create_facility(self, payload: dict) -> dict:
        result = self.db.execute(
            text(
                """
                INSERT INTO Facility (user_id, facility_name, location, sport, description)
                VALUES (:user_id, :facility_name, :location, :sport, :description)
                """
            ),
            payload,
        )
        self.db.commit()
        new_id = result.lastrowid
        return self.get_facility(new_id)

    def update_facility(self, facility_id: int, fields: dict) -> Optional[dict]:
        if not fields:
            return self.get_facility(facility_id)

        set_clause = ", ".join([f"{key} = :{key}" for key in fields.keys()])
        params = fields | {"facility_id": facility_id}
        result = self.db.execute(
            text(f"UPDATE Facility SET {set_clause} WHERE facility_id = :facility_id"),
            params,
        )
        self.db.commit()
        if result.rowcount == 0:
            return None
        return self.get_facility(facility_id)

    def delete_facility(self, facility_id: int) -> bool:
        result = self.db.execute(
            text("DELETE FROM Facility WHERE facility_id = :facility_id"),
            {"facility_id": facility_id},
        )
        self.db.commit()
        return result.rowcount > 0
