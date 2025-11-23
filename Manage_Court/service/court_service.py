from typing import List, Optional

from models.court_models import Court, CourtCreate, CourtUpdate
from repository.court_repo import CourtRepo


class CourtService:
    def __init__(self, repo: CourtRepo):
        self.repo = repo

    def list_courts(self) -> List[Court]:
        return [Court(**item) for item in self.repo.list_courts()]

    def create_court(self, payload: CourtCreate) -> Court:
        record = self.repo.create_court(payload.model_dump())
        return Court(**record)

    def get_court(self, court_id: int) -> Optional[Court]:
        record = self.repo.get_court(court_id)
        return Court(**record) if record else None

    def update_court(self, court_id: int, payload: CourtUpdate) -> Optional[Court]:
        record = self.repo.update_court(court_id, payload.model_dump(exclude_none=True))
        return Court(**record) if record else None

    def delete_court(self, court_id: int) -> bool:
        return self.repo.delete_court(court_id)
