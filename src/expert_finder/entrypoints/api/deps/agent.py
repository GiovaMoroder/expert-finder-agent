"""Agent wiring for API entrypoints."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from expert_finder.application.factory import build_agent
from expert_finder.config.settings import AgentSettings
from expert_finder.config.settings import SupportedModel
from expert_finder.config.settings import get_agent_settings
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent


@lru_cache(maxsize=1)
def _build_cached_agent(model: SupportedModel) -> ExpertFinderAgent:
    return build_agent(settings_provider=lambda: AgentSettings(gpt_model=model))


def get_agent(
    settings: Annotated[AgentSettings, Depends(get_agent_settings)],
) -> ExpertFinderAgent:
    return _build_cached_agent(settings.gpt_model)
