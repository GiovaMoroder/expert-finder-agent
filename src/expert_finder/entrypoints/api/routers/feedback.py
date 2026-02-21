"""Feedback routes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from expert_finder.domain.models.question_logs import ExpertFeedbackEntry
from expert_finder.domain.ports.repositories import ExpertFeedbackRepository
from expert_finder.entrypoints.api.deps import get_expert_feedback_repository_cached, require_bearer_user
from expert_finder.entrypoints.api.schemas.feedback import ExpertFeedbackRequest


router = APIRouter(tags=["feedback"])


@router.post("/api/feedback/expert")
def submit_expert_feedback(
    payload: ExpertFeedbackRequest,
    username: Annotated[str, Depends(require_bearer_user)],
    feedback_repo: Annotated[ExpertFeedbackRepository, Depends(get_expert_feedback_repository_cached)],
) -> dict[str, bool]:
    feedback_repo.append(
        ExpertFeedbackEntry(
            created_at=datetime.now(timezone.utc),
            question_id=payload.question_id,
            username=username,
            expert_key=payload.expert_key,
            expert_name=payload.expert_name,
            expert_linkedin_url=payload.expert_linkedin_url,
            score=payload.score,
            note=payload.note,
        )
    )
    return {"ok": True}

