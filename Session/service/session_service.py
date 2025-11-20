from typing import List
from models.session_models import SessionCreate, SessionDeleteResponse, SessionInfo


class SessionService:
    """Stub session management."""

    def __init__(self):
        self._sample = SessionInfo(
            session_id=1,
            user_id=7,
            device="Chrome",
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
            is_active=True,
        )

    def create_session(self, payload: SessionCreate) -> SessionInfo:
        return SessionInfo(
            session_id=55,
            user_id=payload.user_id,
            device=payload.device,
            ip_address=payload.ip_address,
            user_agent=payload.user_agent,
            is_active=True,
        )

    def list_by_user(self, user_id: int) -> List[SessionInfo]:
        return [
            self._sample.copy(update={"session_id": 1, "user_id": user_id}),
            self._sample.copy(update={"session_id": 2, "user_id": user_id, "device": "Mobile"}),
        ]

    def delete_session(self, session_id: int) -> SessionDeleteResponse:
        return SessionDeleteResponse(
            session_id=session_id,
            message="Stub delete – chưa cập nhật DB",
        )
