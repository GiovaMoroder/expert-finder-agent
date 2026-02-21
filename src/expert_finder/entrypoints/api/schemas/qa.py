"""Schemas for QA endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

from expert_finder.domain.models.experts import FinalResult


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    question_id: str = Field(..., min_length=1)
    question: str
    result: FinalResult

