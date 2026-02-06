from __future__ import annotations

import pandas as pd


def linkedin_date_to_iso(value: object) -> object:
    if isinstance(value, dict):
        year = value.get("year")
        if not year:
            return pd.NA
        month = value.get("month") or 1
        day = value.get("day") or 1
        return f"{year:04d}-{month:02d}-{day:02d}"
    if isinstance(value, str) and value.strip():
        return value
    return pd.NA
