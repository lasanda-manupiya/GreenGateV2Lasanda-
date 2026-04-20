from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt. Simple and reliable for MVP."""
    salt = uuid.uuid4().hex
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt, stored_hash = hashed_password.split("$", 1)
        computed = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return computed == stored_hash
    except (ValueError, AttributeError):
        return False


def create_access_token(user_id: str, organisation_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "org": organisation_id,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str, organisation_id: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "org": organisation_id,
        "type": "refresh",
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises JWTError on failure."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
