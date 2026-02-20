"""JWT token helpers for OAuth2 password flow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from expert_finder.config.settings import ApiSettings
from expert_finder.config.settings import get_api_settings

OAUTH2_ALGORITHM = "HS256"


def create_access_token_with_settings(*, username: str, settings: ApiSettings) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": username, "exp": expire_at}
    return jwt.encode(payload, settings.oauth2_secret_key, algorithm=OAUTH2_ALGORITHM)


def issue_access_token(*, username: str, settings: ApiSettings) -> str:
    return create_access_token_with_settings(username=username, settings=settings)


def create_access_token(*, username: str) -> str:
    return create_access_token_with_settings(username=username, settings=get_api_settings())


def decode_access_token_with_settings(token: str, settings: ApiSettings) -> dict:
    """
    Decode/validate a token and return the JWT payload.

    Raises jose.JWTError on failure.
    """
    return jwt.decode(token, settings.oauth2_secret_key, algorithms=[OAUTH2_ALGORITHM])


def decode_access_token(token: str) -> dict:
    return decode_access_token_with_settings(token, get_api_settings())


__all__ = [
    "JWTError",
    "OAUTH2_ALGORITHM",
    "create_access_token",
    "create_access_token_with_settings",
    "decode_access_token",
    "decode_access_token_with_settings",
    "issue_access_token",
]
