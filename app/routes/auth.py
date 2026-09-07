from fastapi import APIRouter, HTTPException

from app.auth import authenticate_user, create_token
from app.schemas import LoginRequest


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest):
    user = authenticate_user(
        payload.email,
        payload.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": create_token(
            user["user_id"],
            user["tenant_id"],
        ),
        "token_type": "bearer",
    }