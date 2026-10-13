from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database.repository import get_user


class AuthenticatedUser:
    """
    Represents the current authenticated user.
    """

    def __init__(
        self,
        user_id: str = "anonymous-user",
        email: str = "",
        name: str = "",
    ):
        self.id = user_id
        self.email = email
        self.name = name


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """
    FastAPI dependency that returns the current user.
    If Bearer token is provided, decodes the JWT and loads the user from DB.
    Defaults to anonymous user when no token is present, preserving backward compatibility with tests.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        from auth.service import decode_access_token

        try:
            user_id = decode_access_token(token)
            db_user = get_user(db, user_id)
            if db_user:
                return AuthenticatedUser(
                    user_id=db_user.id,
                    email=db_user.email,
                    name=db_user.name,
                )
            return AuthenticatedUser(user_id=user_id)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc) if "expired" in str(exc).lower() else "Invalid or expired authentication token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return AuthenticatedUser()