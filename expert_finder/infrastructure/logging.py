"""Logging utilities for the Expert Finder POC."""

from __future__ import annotations

import logging
import os

# Logger name prefixes we never want at DEBUG (only our app logs at DEBUG)
_THIRD_PARTY_PREFIXES = ("openai", "httpx", "httpcore")


def _silence_third_party_loggers() -> None:
    """Set OpenAI/HTTP stack loggers to INFO so DEBUG shows only our app's logs."""
    root = logging.getLogger()
    for name in list(root.manager.loggerDict):  # type: ignore[union-attr]
        if name.startswith(_THIRD_PARTY_PREFIXES):
            logging.getLogger(name).setLevel(logging.INFO)
    for name in _THIRD_PARTY_PREFIXES:
        logging.getLogger(name).setLevel(logging.INFO)


def silence_third_party_loggers() -> None:
    """Re-apply silencing of OpenAI/HTTP loggers (e.g. after importing the OpenAI SDK)."""
    _silence_third_party_loggers()


def setup_logging(level: str | None = None) -> None:
    """Configure root logging with a consistent format."""
    # Prevent OpenAI SDK from enabling its own debug when imported later
    if os.environ.get("OPENAI_LOG", "").upper() == "DEBUG":
        os.environ["OPENAI_LOG"] = "info"
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
        _silence_third_party_loggers()
        return
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    _silence_third_party_loggers()
