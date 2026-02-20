"""Agent wiring for API entrypoints."""

from __future__ import annotations

import os
from functools import lru_cache

from expert_finder.application.factory import build_agent
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent


def _use_stub_llm() -> bool:
    return os.environ.get("EXPERT_FINDER_USE_STUB_LLM", "").lower() in {"1", "true", "yes"}


@lru_cache(maxsize=1)
def get_agent() -> ExpertFinderAgent:
    return build_agent(use_stub_llm=_use_stub_llm())
