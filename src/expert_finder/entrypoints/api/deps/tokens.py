"""JWT token helpers for OAuth2 password flow."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

OAUTH2_ALGORITHM = "HS256"


def _oauth2_secret_key() -> str:
    secret = os.environ.get("OAUTH2_SECRET_KEY")
    if not isinstance(secret, str) or not secret.strip():
        raise RuntimeError("OAUTH2_SECRET_KEY environment variable is not set")
    return secret


def create_access_token(*, username: str) -> str:
    expires_minutes = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": username, "exp": expire_at}
    return jwt.encode(payload, _oauth2_secret_key(), algorithm=OAUTH2_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode/validate a token and return the JWT payload.

    Raises jose.JWTError on failure.
    """
    return jwt.decode(token, _oauth2_secret_key(), algorithms=[OAUTH2_ALGORITHM])


__all__ = ["JWTError", "OAUTH2_ALGORITHM", "create_access_token", "decode_access_token"]
