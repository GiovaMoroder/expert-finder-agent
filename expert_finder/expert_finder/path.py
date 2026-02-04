from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"

RAW_EDUCATION_CSV = DATA_DIR / "raw" / "education.csv"
PROCESSED_EDUCATION_CSV = DATA_DIR / "processed" / "education.csv"
EDUCATION_CSV = PROCESSED_EDUCATION_CSV

RAW_WORK_EXPERIENCES_CSV = DATA_DIR / "raw" / "work_experiences.csv"
PROCESSED_WORK_EXPERIENCES_CSV = DATA_DIR / "processed" / "work_experiences.csv"
WORK_EXPERIENCES_CSV = PROCESSED_WORK_EXPERIENCES_CSV
PROFESSIONAL_CSV = WORK_EXPERIENCES_CSV
MENTEES_JSON = DATA_DIR / "mentees.json"
INSTITUTIONS_JSON = DATA_DIR / "institutions.json"
