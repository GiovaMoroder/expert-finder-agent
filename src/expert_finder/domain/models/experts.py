"""Pydantic schemas for LLM IO and domain types."""

from __future__ import annotations

from typing import Literal
from typing import Optional

from pydantic import BaseModel, Field


class RankingRule(BaseModel):
    weight: float = Field(..., ge=0.0, description="Non-negative weight for this ranking signal")
    keyword: str = Field(..., min_length=1, description="Keyword used to score this column")


class QueryExtraction(BaseModel):
    tool_required: bool = Field(..., description="Whether a tool should be called")
    filter_column: Optional[str] = Field(default=None, description="Single column name used for filtering")
    filter_value: Optional[str] = Field(default=None, description="Value used to filter in filter_column")
    sort_by: Optional[str] = Field(default=None, description="Column name to sort by")
    sort_order: Literal["asc", "desc"] | None = Field(
        default=None,
        description="Sort direction. Must be 'asc' or 'desc' when sort_by is set.",
    )
    ranking: dict[str, RankingRule] | None = Field(
        default=None,
        description="Optional weighted ranking rules keyed by column name",
    )


class FinalExpert(BaseModel):
    name: str
    reason: str
    profile: Optional[dict] = None


class FinalResult(BaseModel):
    experts: list[FinalExpert] = Field(..., min_length=0, max_length=3)

class AskQuestionResult(BaseModel):
    question: str
    result: FinalResult
