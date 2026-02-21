"""Application service used by CLI and API entrypoints."""

from __future__ import annotations

from expert_finder.application.deps import get_agent
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.models.experts import AskQuestionResult




def ask_question(
    question: str,
    agent: ExpertFinderAgent | None = None,
) -> AskQuestionResult:
    """Run the expert finder and return the user-facing response payload."""
    selected_agent = agent or get_agent()
    result = selected_agent.run(question)
    return AskQuestionResult(question=question, result=result)
