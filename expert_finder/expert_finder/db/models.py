from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WorkExperienceRecord:
    full_name: str
    company: Optional[str]
    role: Optional[str]
    location: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    description: Optional[str]


@dataclass(frozen=True)
class EducationRecord:
    full_name: str
    institution: Optional[str]
    degree: Optional[str]
    field_of_study: Optional[str]
    start_date: Optional[str]
    graduation_date: Optional[str]
    gpa: Optional[str]
