"""Application service used by CLI and API entrypoints."""

from __future__ import annotations

from expert_finder.application.deps import get_agent
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent


def ask_question(question: str, agent: ExpertFinderAgent | None = None) -> dict[str, object]:
    """Run the expert finder and return the user-facing response payload."""
    selected_agent = agent or get_agent()
    result = selected_agent.run(question)
    formatted_results = [{"name": expert.name, "reason": expert.reason} for expert in result.experts]
    return {"question": question, "result": formatted_results}
