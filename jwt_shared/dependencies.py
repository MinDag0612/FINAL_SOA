from fastapi import Depends, HTTPException
from jwt_shared.jwt import jwt_services

# Initialize JWT service once
_jwt_service = jwt_services()


def get_current_user(token: str = Depends(_jwt_service.oauth2_scheme)):
    try:
        payload = _jwt_service.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_id(user: dict = Depends(get_current_user)) -> int:
    """Extract user ID from current user."""
    return int(user.get("sub"))


def get_user_email(user: dict = Depends(get_current_user)) -> str:
    """Extract user email from current user."""
    return user.get("infor", {}).get("email", "")


def get_user_role(user: dict = Depends(get_current_user)) -> str:
    """Extract user role from current user."""
    return user.get("infor", {}).get("role", "user")
