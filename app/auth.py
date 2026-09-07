from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from app.config import settings
from app.db import get_connection


password_hash = PasswordHash.recommended()
security = HTTPBearer()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(user_id: UUID, tenant_id: UUID) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
        )

        return {
            "user_id": UUID(payload["sub"]),
            "tenant_id": UUID(payload["tenant_id"]),
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def authenticate_user(email: str, password: str):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, tenant_id, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,),
        ).fetchone()

    if not row or not verify_password(password, row[2]):
        return None

    return {
        "user_id": row[0],
        "tenant_id": row[1],
    }