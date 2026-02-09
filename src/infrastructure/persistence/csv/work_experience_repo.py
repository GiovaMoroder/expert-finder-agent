from __future__ import annotations

from pathlib import Path
from typing import Iterable

from expert_finder.infrastructure.persistence.csv.csv_base import CsvRepositoryBase
from expert_finder.domain.models import WorkExperienceRecord
from expert_finder.domain.ports import WorkExperienceRepository
from expert_finder.infrastructure.path import WORK_EXPERIENCES_CSV


class CsvWorkExperienceRepository(CsvRepositoryBase, WorkExperienceRepository):
    SEARCH_COLUMNS = ("company",)

    def __init__(self, csv_path: Path = WORK_EXPERIENCES_CSV) -> None:
        super().__init__(csv_path)

    def list_all(self) -> Iterable[WorkExperienceRecord]:
        df = self._load()
        for _, row in df.iterrows():
            yield WorkExperienceRecord(
                full_name=row.get("full_name"),
                company=row.get("company"),
                role=row.get("role"),
                location=row.get("location"),
                start_date=row.get("start_date"),
                end_date=row.get("end_date"),
                description=row.get("description"),
            )

    def find_by_company(self, company: str) -> list[WorkExperienceRecord]:
        df = self._load()
        if "company" not in df.columns:
            return []

        mask = df["company"].fillna("").str.contains(company, case=False, na=False)
        matches = df[mask]
        results: list[WorkExperienceRecord] = []
        for _, row in matches.iterrows():
            results.append(
                WorkExperienceRecord(
                    full_name=row.get("full_name"),
                    company=row.get("company"),
                    role=row.get("role"),
                    location=row.get("location"),
                    start_date=row.get("start_date"),
                    end_date=row.get("end_date"),
                    description=row.get("description"),
                )
            )
        return results

    def search(self, query: str, top_k: int = 10, min_score: float = 0.0) -> list[str]:
        df = self._load()
        self._apply_norm_columns(df, self.SEARCH_COLUMNS)
        return self._search_dataframe(df, query, self.SEARCH_COLUMNS, top_k, min_score)
