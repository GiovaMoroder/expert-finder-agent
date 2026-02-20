"""JWT token helpers for OAuth2 password flow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from expert_finder.config.settings import get_api_settings

OAUTH2_ALGORITHM = "HS256"


def _oauth2_secret_key() -> str:
    return get_api_settings().oauth2_secret_key


def create_access_token(*, username: str) -> str:
    expires_minutes = get_api_settings().access_token_expire_minutes
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
