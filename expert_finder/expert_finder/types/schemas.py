"""Pydantic schemas for LLM IO and domain types."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

class Candidate(BaseModel):
    name: str
    current_title: Optional[str] = None
    institution_records: Optional[list[dict]]



class QueryExtraction(BaseModel):
    tool_required: bool = Field(..., description="Whether a tool should be called")
    institution: Optional[str] = Field(default=None, description="Target company or school")
    role: Optional[str] = Field(default=None, description="Target role, if present")
    topic: Optional[str] = Field(default=None, description="Short topic, if present")


class FinalExpert(BaseModel):
    name: str
    reason: str


class FinalResult(BaseModel):
    experts: list[FinalExpert] = Field(..., min_length=0, max_length=3)
