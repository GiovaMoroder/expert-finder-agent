"""Agent wiring for API entrypoints."""

from __future__ import annotations

from functools import lru_cache

from expert_finder.application.deps import get_agent
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent


@lru_cache(maxsize=1)
def get_agent_cached() -> ExpertFinderAgent:
    """Return a process-wide agent instance for API requests."""
    return get_agent()
