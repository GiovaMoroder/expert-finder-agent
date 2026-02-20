"""Persistence dependencies (composition) for API entrypoints."""

from __future__ import annotations

from functools import lru_cache

from expert_finder.domain.ports.repositories import QuestionLogRepository
from expert_finder.config.settings import get_api_settings
from expert_finder.infrastructure.persistence.sqlalchemy.question_logs_repo import (
    SqlAlchemyQuestionLogRepository,
)


@lru_cache(maxsize=1)
def get_question_log_repository() -> QuestionLogRepository:
    """
    Return the configured QuestionLogRepository implementation.

    This is the swapping point for alternate persistence backends.
    """
    settings = get_api_settings()
    return SqlAlchemyQuestionLogRepository(db_url=settings.question_logs_db_url)
