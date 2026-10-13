import os
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database.repository import create_user, get_user_by_email
from models.schemas import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)


SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-secret-key",
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hash.hash(password)


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(
        password,
        stored_hash,
    )


def create_access_token(
    user_id: str,
) -> str:
    """Create a JWT access token for a user."""
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": user_id,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> str:
    """Decode a JWT and return its user ID."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError(
            "Invalid or expired token."
        ) from exc

    user_id = payload.get("sub")

    if not user_id or not isinstance(user_id, str):
        raise ValueError(
            "Invalid authentication token."
        )

    return user_id


def signup(
    db: Session,
    request: SignupRequest,
) -> TokenResponse:
    """Create a user account and return an access token."""
    email = request.email.strip().lower()

    if get_user_by_email(
        db,
        email,
    ):
        raise ValueError(
            "An account with this email already exists."
        )

    user = create_user(
        db=db,
        user_id=str(uuid.uuid4()),
        name=request.name.strip(),
        email=email,
        password_hash=hash_password(
            request.password
        ),
    )

    token = create_access_token(
        user.id
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
        ),
    )


def login(
    db: Session,
    request: LoginRequest,
) -> TokenResponse:
    """Authenticate a user and return an access token."""
    email = request.email.strip().lower()

    user = get_user_by_email(
        db,
        email,
    )

    if not user or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise ValueError(
            "Invalid email or password."
        )

    token = create_access_token(
        user.id
    )

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
        ),
    )