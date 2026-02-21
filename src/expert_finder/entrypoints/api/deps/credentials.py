"""Credential validation for API authentication."""

from __future__ import annotations

import re

from fastapi import HTTPException

USERNAME_REGEX = re.compile(r"^[A-Za-z]+_[A-Za-z]+$")


def validate_credentials(username: str, password: str, *, expected_password: str) -> None:
    if not USERNAME_REGEX.match(username):
        raise HTTPException(status_code=400, detail="Username must match name_surname.")
    if password != expected_password:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
