"""Logging utilities for the Expert Finder POC."""

from __future__ import annotations

import logging
import os


def setup_logging(level: str | None = None) -> None:
    """Configure root logging with a consistent format."""
    resolved_level = (level or os.environ.get("LOG_LEVEL") or "INFO").upper()
    numeric_level = getattr(logging, resolved_level, None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        )
        logging.getLogger(__name__).warning(
            "Unknown log level %r. Falling back to INFO.", resolved_level
        )
        return
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
