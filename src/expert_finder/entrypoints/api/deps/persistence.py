"""Persistence dependencies (composition) for API entrypoints."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from expert_finder.domain.ports.repositories import QuestionLogRepository
from expert_finder.infrastructure.persistence.sqlalchemy.question_logs_repo import (
    SqlAlchemyQuestionLogRepository,
)


@lru_cache(maxsize=1)
def get_question_log_repository() -> QuestionLogRepository:
    """
    Return the configured QuestionLogRepository implementation.

    This is the swapping point for alternate persistence backends.
    """
    backend = os.environ.get("EXPERT_FINDER_BACKEND").lower()
    if backend != "sqlalchemy":
        raise RuntimeError(f"Unsupported question log backend: {backend!r}")

    db_path = Path(os.environ.get("EXPERT_FINDER_DB_PATH"))
    return SqlAlchemyQuestionLogRepository(db_path=db_path)

