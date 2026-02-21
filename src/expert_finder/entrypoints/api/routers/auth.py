"""Authentication routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from expert_finder.config.settings import ApiSettings
from expert_finder.config.settings import get_api_settings
from expert_finder.entrypoints.api.deps import issue_access_token, validate_credentials


router = APIRouter(tags=["core"])


def validate_form_credentials(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> str:
    username = form_data.username.strip()
    validate_credentials(
        username=username,
        password=form_data.password,
        expected_password=settings.app_test_password,
    )
    return username


@router.post("/token")
def token(
    response: Response,
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
    username: Annotated[str, Depends(validate_form_credentials)],
) -> dict[str, str]:
    """
    OAuth2 Password Flow token endpoint.

    Returns a JWT access token that can be used as:
    - Authorization: Bearer <token> (API clients, /docs)
    - HttpOnly cookie "access_token" (browser UI convenience)
    """
    access_token = issue_access_token(username=username, settings=settings)
    response.set_cookie(
        key="access_token",
        value=access_token,
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return {"access_token": access_token, "token_type": "bearer"}
