from __future__ import annotations

import re
from typing import Iterable


def normalize_institution(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", name or "").strip()
    return cleaned


def _extract_from_records(records: Iterable[dict]) -> list[str]:
    values: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        institution = record.get("institution")
        if institution:
            values.append(str(institution))
    return values


def extract_institutions(record: dict) -> list[str]:
    """Extract institution names from a mentee record."""
    values: list[str] = []

    for key in ("institution", "current_institution", "current_company", "company"):
        if key in record and record[key]:
            values.append(str(record[key]))

    for key in ("institution_records", "education", "work_history", "employment"):
        if key in record and isinstance(record[key], list):
            values.extend(_extract_from_records(record[key]))

    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        cleaned = normalize_institution(value)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        normalized.append(cleaned)

    return normalized
