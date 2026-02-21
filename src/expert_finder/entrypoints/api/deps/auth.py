"""FastAPI auth dependencies (Bearer header and/or HttpOnly cookie)."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from expert_finder.entrypoints.api.deps.tokens import JWTError, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def _extract_access_token_from_cookie(request: Request) -> str | None:
    raw = request.cookies.get("access_token")
    if not isinstance(raw, str) or not raw:
        return None
    # Allow either a raw token or a "Bearer <token>" value.
    if raw.lower().startswith("bearer "):
        raw = raw[7:].strip()
    return raw or None


def current_user(request: Request) -> str | None:
    """
    UI helper: returns the username from an access token cookie, if present.
    """
    token = _extract_access_token_from_cookie(request)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except JWTError:
        return None
    username = payload.get("sub")
    return username if isinstance(username, str) and username else None


def require_bearer_user(request: Request, token: str | None = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        token = _extract_access_token_from_cookie(request)
    if not token:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise credentials_exception from exc

    username = payload.get("sub")
    if not isinstance(username, str) or not username:
        raise credentials_exception
    return username
