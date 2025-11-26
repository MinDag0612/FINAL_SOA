import json
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from Facility.models.facility_models import Facility, FacilityCreate, FacilityUpdate


class FacilityRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_facilities(self) -> List[Facility]:
        query = text(
            """
            SELECT facility_id, user_id, name, address, sport, description,
                   opening_hours, contact_phone, amenities, is_active
            FROM Facility
            WHERE is_active = 1
            ORDER BY facility_id
            """
        )
        rows = self.db.execute(query).mappings().all()
        return [self._row_to_model(row) for row in rows]

    def get_facility(self, facility_id: int) -> Optional[Facility]:
        query = text(
            """
            SELECT facility_id, user_id, name, address, sport, description,
                   opening_hours, contact_phone, amenities, is_active
            FROM Facility
            WHERE facility_id = :facility_id
            """
        )
        row = self.db.execute(query, {"facility_id": facility_id}).mappings().first()
        if not row:
            return None
        return self._row_to_model(row)

    def create_facility(self, payload: FacilityCreate) -> Facility:
        query = text(
            """
            INSERT INTO Facility (user_id, name, address, sport, description, opening_hours, contact_phone, amenities, is_active)
            VALUES (:user_id, :name, :address, :sport, :description, :opening_hours, :contact_phone, :amenities, :is_active)
            """
        )
        amenities = json.dumps(payload.amenities or [])
        result = self.db.execute(
            query,
            {
                "user_id": payload.user_id,
                "name": payload.name,
                "address": payload.address,
                "sport": payload.sport,
                "description": payload.description,
                "opening_hours": payload.opening_hours,
                "contact_phone": payload.contact_phone,
                "amenities": amenities,
                "is_active": 1,
            },
        )
        self.db.commit()
        facility_id = result.lastrowid
        return self.get_facility(facility_id)

    def update_facility(self, facility_id: int, payload: FacilityUpdate) -> Optional[Facility]:
        fields = payload.model_dump(exclude_none=True)
        if not fields:
            return self.get_facility(facility_id)

        set_clauses = []
        params = {"facility_id": facility_id}
        for key, value in fields.items():
            if key == "amenities":
                value = json.dumps(value)
            set_clauses.append(f"{key} = :{key}")
            params[key] = value

        query = text(
            f"""
            UPDATE Facility
            SET {", ".join(set_clauses)}
            WHERE facility_id = :facility_id
            """
        )
        self.db.execute(query, params)
        self.db.commit()
        return self.get_facility(facility_id)

    def delete_facility(self, facility_id: int) -> bool:
        query = text(
            """
            UPDATE Facility
            SET is_active = 0
            WHERE facility_id = :facility_id
            """
        )
        result = self.db.execute(query, {"facility_id": facility_id})
        self.db.commit()
        return result.rowcount > 0

    def _row_to_model(self, row) -> Facility:
        amenities_raw = row.get("amenities")
        amenities = json.loads(amenities_raw) if amenities_raw else []
        return Facility(
            facility_id=row["facility_id"],
            user_id=row["user_id"],
            name=row["name"],
            address=row["address"] or "",
            sport=row.get("sport"),
            description=row.get("description"),
            opening_hours=row.get("opening_hours"),
            contact_phone=row.get("contact_phone"),
            amenities=amenities,
            is_active=bool(row.get("is_active", 1)),
        )

#------------------FOR MANAGER FLOW----------------------------------
    def get_facilities_by_manager(self, manager_id: int) -> List[str]:
        try:
            query = text(
                """
                SELECT facility_id, name
                FROM Facility
                WHERE user_id = :manager_id AND is_active = 1
                ORDER BY facility_id
                """
            )
            result = self.db.execute(
                query,
                {"manager_id": manager_id}
            )
            rows = result.mappings().all()
            return [f"{row['facility_id']}: {row['name']}" for row in rows]
        except Exception as e:
            raise {"error": str(e) + " -- from facility repository"}