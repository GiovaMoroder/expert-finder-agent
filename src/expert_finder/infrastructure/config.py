"""Compatibility wrapper for agent settings."""

from __future__ import annotations

from dataclasses import dataclass

from expert_finder.config.settings import get_agent_settings


@dataclass(frozen=True, slots=True)
class Settings:
    gpt_model: str


SETTINGS = Settings(gpt_model=get_agent_settings().gpt_model)
