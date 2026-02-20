"""Persistence dependencies (composition) for API entrypoints."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from expert_finder.config.settings import ApiSettings
from expert_finder.domain.ports.repositories import QuestionLogRepository
from expert_finder.config.settings import get_api_settings
from expert_finder.infrastructure.persistence.sqlalchemy.question_logs_repo import (
    SqlAlchemyQuestionLogRepository,
)


@lru_cache(maxsize=1)
def _build_cached_question_log_repository(db_url: str) -> QuestionLogRepository:
    return SqlAlchemyQuestionLogRepository(db_url=db_url)


def get_question_log_repository(
    settings: Annotated[ApiSettings, Depends(get_api_settings)],
) -> QuestionLogRepository:
    """
    Return the configured QuestionLogRepository implementation.

    This is the swapping point for alternate persistence backends.
    """
    return _build_cached_question_log_repository(settings.question_logs_db_url)
