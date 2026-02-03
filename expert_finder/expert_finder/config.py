"""Configuration for the Expert Finder POC."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings.

    In production, these would be loaded from env vars or a config file.
    """

    llm_mode: str = "stub"  # "stub" or "gpt"
    gpt_model: str = "gpt-4o-mini"
    gpt_api_key: str = ""  # TODO: load from env in production


SETTINGS = Settings()
