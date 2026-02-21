"""Question-answering routes."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from expert_finder.application.service import ask_question
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.models.question_logs import QuestionLogEntry
from expert_finder.domain.models.experts import AskQuestionResult
from expert_finder.domain.ports.repositories import QuestionLogRepository
from expert_finder.entrypoints.api.deps import (
    get_agent_cached,
    get_question_log_repository_cached,
    require_bearer_user,
)
from expert_finder.entrypoints.api.schemas.qa import AskRequest


router = APIRouter(tags=["core"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/ask")
def api_ask(
    payload: AskRequest,
    username: Annotated[str, Depends(require_bearer_user)],
    agent: Annotated[ExpertFinderAgent, Depends(get_agent_cached)],
    question_logs: Annotated[QuestionLogRepository, Depends(get_question_log_repository_cached)],
) -> AskQuestionResult:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    created_at = datetime.now(timezone.utc)
    started = perf_counter()
    try:
        result = ask_question(question, agent=agent)
        latency_ms = int((perf_counter() - started) * 1000)
        try:
            question_logs.append(
                QuestionLogEntry(
                    created_at=created_at,
                    username=username,
                    question=question,
                    status="ok",
                    latency_ms=latency_ms,
                )
            )
        except Exception as log_exc:
            # Logging must not break the main endpoint.
            print(f"Error logging question: {log_exc}")
        return result
    except Exception as exc:
        latency_ms = int((perf_counter() - started) * 1000)
        try:
            question_logs.append(
                QuestionLogEntry(
                    created_at=created_at,
                    username=username,
                    question=question,
                    status="error",
                    latency_ms=latency_ms,
                    error_message=str(exc),
                )
            )
        except Exception as log_exc:
            # Logging must not break the main endpoint.
            print(f"Error logging question: {log_exc}")
        raise
