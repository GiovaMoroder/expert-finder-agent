"""Agent wiring for API entrypoints."""

from __future__ import annotations

from functools import lru_cache

from expert_finder.application.factory import build_agent
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent


@lru_cache(maxsize=1)
def get_agent() -> ExpertFinderAgent:
    return build_agent()
