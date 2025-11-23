import json
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
                SELECT facility_id, user_id, facility_name, location, sport, description, amenities
                FROM Facility
                ORDER BY facility_id
                """
            )
        )
        return [self._row_to_dict(row) for row in result]

    def get_facility(self, facility_id: int) -> Optional[dict]:
        row = (
            self.db.execute(
                text(
                    """
                    SELECT facility_id, user_id, facility_name, location, sport, description, amenities
                    FROM Facility
                    WHERE facility_id = :facility_id
                    """
                ),
                {"facility_id": facility_id},
            )
            .mappings()
            .first()
        )
        return self._row_to_dict(row) if row else None

    def create_facility(self, payload: dict) -> dict:
        result = self.db.execute(
            text(
                """
                INSERT INTO Facility (user_id, facility_name, location, sport, amenities, description)
                VALUES (:user_id, :facility_name, :location, :sport, :amenities, :description)
                """
            ),
            self._with_serialized_amenities(payload),
        )
        self.db.commit()
        new_id = result.lastrowid
        return self.get_facility(new_id)

    def update_facility(self, facility_id: int, fields: dict) -> Optional[dict]:
        if not fields:
            return self.get_facility(facility_id)

        set_clause = ", ".join([f"{key} = :{key}" for key in fields.keys()])
        params = self._with_serialized_amenities(fields) | {"facility_id": facility_id}
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

    def _row_to_dict(self, row) -> dict:
        if row is None:
            return None
        data = dict(row._mapping)
        # amenities stored as JSON, convert to list if not None
        if data.get("amenities") is not None and isinstance(data["amenities"], str):
            try:
                data["amenities"] = json.loads(data["amenities"])
            except Exception:
                pass
        return data

    def _with_serialized_amenities(self, payload: dict) -> dict:
        payload = payload.copy()
        if "amenities" in payload and payload["amenities"] is not None:
            payload["amenities"] = json.dumps(payload["amenities"])
        return payload
