"""Authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from expert_finder.entrypoints.api.deps import create_access_token, validate_login_credentials
from expert_finder.config.settings import get_api_settings


router = APIRouter(tags=["core"])


@router.post("/token")
def token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    """
    OAuth2 Password Flow token endpoint.

    Returns a JWT access token that can be used as:
    - Authorization: Bearer <token> (API clients, /docs)
    - HttpOnly cookie "access_token" (browser UI convenience)
    """
    username = form_data.username.strip()
    password = form_data.password
    validate_login_credentials(username=username, password=password)
    access_token = create_access_token(username=username)
    response.set_cookie(
        key="access_token",
        value=access_token,
        secure=get_api_settings().cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return {"access_token": access_token, "token_type": "bearer"}
