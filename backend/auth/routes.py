from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import AuthenticatedUser, get_current_user
from auth.service import login, signup
from database.connection import get_db
from models.schemas import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.post("/signup", response_model=TokenResponse)
def signup_endpoint(
    request: SignupRequest,
    db: Session = Depends(get_db),
):
    try:
        return signup(db, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@auth_router.post("/login", response_model=TokenResponse)
def login_endpoint(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return login(db, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@auth_router.get("/me", response_model=UserResponse)
def get_me_endpoint(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        name=getattr(current_user, "name", "User"),
        email=getattr(current_user, "email", ""),
    )

