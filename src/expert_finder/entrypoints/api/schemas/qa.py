"""Schemas for QA endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)

