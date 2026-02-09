from __future__ import annotations

from pathlib import Path

# File is at: <repo>/src/expert_finder/infrastructure/path.py
# parents[0]=infrastructure, [1]=expert_finder, [2]=src, [3]=<repo>
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"

RAW_EDUCATION_CSV = DATA_DIR / "raw" / "education.csv"
PROCESSED_EDUCATION_CSV = DATA_DIR / "processed" / "education.csv"
EDUCATION_CSV = PROCESSED_EDUCATION_CSV

RAW_WORK_EXPERIENCES_CSV = DATA_DIR / "raw" / "work_experiences.csv"
PROCESSED_WORK_EXPERIENCES_CSV = DATA_DIR / "processed" / "work_experiences.csv"
WORK_EXPERIENCES_CSV = PROCESSED_WORK_EXPERIENCES_CSV
PROFESSIONAL_CSV = WORK_EXPERIENCES_CSV
SAMPLE_REQUESTS_JSON = DATA_DIR / "sample_requests.json"
SAMPLE_REQUESTS_RESULTS_JSON = DATA_DIR / "sample_requests_results.json"
MENTEES_JSON = DATA_DIR / "mentees.json"
