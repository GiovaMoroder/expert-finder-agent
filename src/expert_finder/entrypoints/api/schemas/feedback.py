from __future__ import annotations

from pydantic import BaseModel, Field


class ExpertFeedbackRequest(BaseModel):
    question_id: str = Field(..., min_length=1)
    expert_key: str = Field(..., min_length=1)
    expert_name: str = Field(..., min_length=1)
    expert_linkedin_url: str | None = None
    score: int = Field(..., ge=1, le=3)
    note: str | None = Field(default=None, max_length=2000)


class QuestionFeedbackRequest(BaseModel):
    question_id: str = Field(..., min_length=1)
    note: str = Field(..., min_length=1, max_length=2000)

