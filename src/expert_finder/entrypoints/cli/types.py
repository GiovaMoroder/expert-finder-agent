"""Types shared by CLI modules."""

from __future__ import annotations

from enum import Enum


class OutputFormat(str, Enum):
    json = "json"
    table = "table"
    both = "both"
