from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class QuestionLogEntry:
    question_id: str
    created_at: datetime
    username: str
    question: str
    status: Literal["ok", "error"]
    latency_ms: int
    error_message: str | None = None


@dataclass(frozen=True)
class ExpertFeedbackEntry:
    created_at: datetime
    question_id: str
    username: str
    expert_key: str
    expert_name: str
    expert_linkedin_url: str | None
    score: int
    note: str | None = None

