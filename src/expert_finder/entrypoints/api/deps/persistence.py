"""Persistence dependencies (composition) for API entrypoints."""

from __future__ import annotations

from functools import lru_cache

from expert_finder.application.deps import get_question_log_repository as build_question_log_repository
from expert_finder.domain.ports.repositories import QuestionLogRepository


@lru_cache(maxsize=1)
def get_question_log_repository_cached() -> QuestionLogRepository:
    return build_question_log_repository()
