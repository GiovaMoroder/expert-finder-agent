"""Configuration for the Expert Finder POC."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings.

    In production, these would be loaded from env vars or a config file.
    """

    # TODO: flag here if we want to use different LLMs
    gpt_model: str = "gpt-4o-mini"


SETTINGS = Settings()
