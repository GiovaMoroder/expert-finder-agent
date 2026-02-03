"""Pydantic schemas for LLM IO and domain types."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class InstitutionRecord(BaseModel):
    institution: str
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Candidate(BaseModel):
    name: str
    current_title: Optional[str] = None
    institution_records: Optional[list[InstitutionRecord]]


class CV(BaseModel):
    name: str
    summary: str
    experience: list[str]
    skills: list[str]
    education: list[str]
    publications: list[str]


class QueryExtraction(BaseModel):
    tool_required: bool = Field(..., description="Whether a tool should be called")
    institution: Optional[str] = Field(default=None, description="Target company or school")
    role: Optional[str] = Field(default=None, description="Target role, if present")
    topic: Optional[str] = Field(default=None, description="Short topic, if present")


class ShortlistResult(BaseModel):
    candidate_names: list[str] = Field(..., min_length=0, max_length=7)


class FinalExpert(BaseModel):
    name: str
    reason: str


class FinalResult(BaseModel):
    experts: list[FinalExpert] = Field(..., min_length=0, max_length=3)
