from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"

EDUCATION_CSV = DATA_DIR / "education.csv"
PROFESSIONAL_CSV = DATA_DIR / "professional_activities.csv"
MENTEES_JSON = DATA_DIR / "mentees.json"
INSTITUTIONS_JSON = DATA_DIR / "institutions.json"
