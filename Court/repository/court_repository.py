import json
from typing import List, Optional
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

from Court.models.court_models import Court, CourtCreate, CourtUpdate


class CourtRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_courts(self) -> List[Court]:
        query = text(
            """
            SELECT court_id, facility_id, name, surface_type, hourly_rate, description, available_hours, is_active
            FROM Court
            WHERE is_active = 1
            ORDER BY court_id
            """
        )
        rows = self.db.execute(query).mappings().all()
        return [self._row_to_model(row) for row in rows]

    def list_by_facility(self, facility_id: int) -> List[Court]:
        query = text(
            """
            SELECT court_id, facility_id, name, surface_type, hourly_rate, description, available_hours, is_active
            FROM Court
            WHERE is_active = 1 AND facility_id = :facility_id
            ORDER BY court_id
            """
        )
        rows = self.db.execute(query, {"facility_id": facility_id}).mappings().all()
        return [self._row_to_model(row) for row in rows]

    def get_court(self, court_id: int) -> Optional[Court]:
        query = text(
            """
            SELECT court_id, facility_id, name, surface_type, hourly_rate, description, available_hours, is_active
            FROM Court
            WHERE court_id = :court_id
            """
        )
        row = self.db.execute(query, {"court_id": court_id}).mappings().first()
        if not row:
            return None
        return self._row_to_model(row)

    def create_court(self, payload: CourtCreate) -> Court:
        query = text(
            """
            INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, available_hours, is_active)
            VALUES (:facility_id, :name, :surface_type, :hourly_rate, :description, :available_hours, :is_active)
            """
        )
        result = self.db.execute(
            query,
            {
                "facility_id": payload.facility_id,
                "name": payload.name,
                "surface_type": payload.surface_type,
                "hourly_rate": payload.hourly_rate,
                "description": payload.description,
                "available_hours": json.dumps(payload.available_hours or []),
                "is_active": 1,
            },
        )
        self.db.commit()
        court_id = result.lastrowid
        return self.get_court(court_id)

    def update_court(self, court_id: int, payload: CourtUpdate) -> Optional[Court]:
        fields = payload.model_dump(exclude_none=True)
        if not fields:
            return self.get_court(court_id)

        set_clauses = []
        params = {"court_id": court_id}
        for key, value in fields.items():
            if key == "available_hours":
                value = json.dumps(value)
            set_clauses.append(f"{key} = :{key}")
            params[key] = value

        query = text(
            f"""
            UPDATE Court
            SET {", ".join(set_clauses)}
            WHERE court_id = :court_id
            """
        )
        self.db.execute(query, params)
        self.db.commit()
        return self.get_court(court_id)

    def delete_court(self, court_id: int) -> bool:
        query = text(
            """
            UPDATE Court
            SET is_active = 0
            WHERE court_id = :court_id
            """
        )
        result = self.db.execute(query, {"court_id": court_id})
        self.db.commit()
        return result.rowcount > 0

    def _row_to_model(self, row) -> Court:
        available_raw = row.get("available_hours")
        available_hours = json.loads(available_raw) if available_raw else []
        return Court(
            court_id=row["court_id"],
            facility_id=row["facility_id"],
            name=row["name"],
            surface_type=row.get("surface_type"),
            hourly_rate=float(row["hourly_rate"]) if row.get("hourly_rate") is not None else None,
            description=row.get("description"),
            available_hours=available_hours,
            is_active=bool(row.get("is_active", 1)),
        )
#------------------FOR MANAGER FLOW----------------------------------
    def get_courts_by_facility(self, facility_id: int) -> List[Court]:
        try:
            facility_id = int(facility_id)
            return self.list_by_facility(facility_id)
        except ValueError:
            raise ValueError("Invalid facility ID")
