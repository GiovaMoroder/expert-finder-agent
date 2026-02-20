from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class QuestionLogEntry:
    created_at: datetime
    username: str
    question: str
    status: Literal["ok", "error"]
    latency_ms: int
    error_message: str | None = None

