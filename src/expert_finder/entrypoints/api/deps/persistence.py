"""Persistence dependencies (composition) for API entrypoints."""

from __future__ import annotations

from functools import lru_cache

from expert_finder.application.deps import get_expert_feedback_repository as build_expert_feedback_repository
from expert_finder.application.deps import get_question_feedback_repository as build_question_feedback_repository
from expert_finder.application.deps import get_question_log_repository as build_question_log_repository
from expert_finder.domain.ports.repositories import ExpertFeedbackRepository
from expert_finder.domain.ports.repositories import QuestionFeedbackRepository
from expert_finder.domain.ports.repositories import QuestionLogRepository


@lru_cache(maxsize=1)
def get_question_log_repository_cached() -> QuestionLogRepository:
    return build_question_log_repository()


@lru_cache(maxsize=1)
def get_expert_feedback_repository_cached() -> ExpertFeedbackRepository:
    return build_expert_feedback_repository()


@lru_cache(maxsize=1)
def get_question_feedback_repository_cached() -> QuestionFeedbackRepository:
    return build_question_feedback_repository()
