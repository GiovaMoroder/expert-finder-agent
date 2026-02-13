from __future__ import annotations

from pathlib import Path
from typing import Iterable
from typing import Literal

import pandas as pd

from expert_finder.infrastructure.persistence.csv.csv_base import CsvRepositoryBase
from expert_finder.domain.models import EducationRecord, RankingRule
from expert_finder.domain.ports import EducationRepository
from expert_finder.infrastructure.path import EDUCATION_CSV


class CsvEducationRepository(CsvRepositoryBase, EducationRepository):
    SEARCH_COLUMNS = ("full_name", "institution", "field_of_study", "degree")

    def __init__(self, csv_path: Path = EDUCATION_CSV) -> None:
        super().__init__(csv_path)

    def list_all(self) -> Iterable[EducationRecord]:
        df = self._load()
        for _, row in df.iterrows():
            yield EducationRecord(
                full_name=row.get("full_name"),
                institution=row.get("institution"),
                degree=row.get("degree"),
                field_of_study=row.get("field_of_study"),
                start_date=row.get("start_date"),
                end_date=row.get("end_date"),
                gpa=row.get("gpa"),
            )

    def find_by_institution(self, institution: str) -> list[EducationRecord]:
        df = self._load()
        if "institution" not in df.columns:
            return []

        mask = df["institution"].fillna("").str.contains(institution, case=False, na=False)
        matches = df[mask]
        results: list[EducationRecord] = []
        for _, row in matches.iterrows():
            results.append(
                EducationRecord(
                    full_name=row.get("full_name"),
                    institution=row.get("institution"),
                    degree=row.get("degree"),
                    field_of_study=row.get("field_of_study"),
                    start_date=row.get("start_date"),
                    end_date=row.get("end_date"),
                    gpa=row.get("gpa"),
                )
            )
        return results

    def search(
        self,
        filter_column: str | None = None,
        filter_value: str | None = None,
        top_k: int = 10,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
        ranking: dict[str, RankingRule] | None = None,
    ) -> list[str]:
        df = self._load()
        return self._search_dataframe(
            df,
            filter_column=filter_column,
            filter_value=filter_value,
            top_k=top_k,
            min_score=min_score,
            sort_by=sort_by,
            sort_order=sort_order,
            ranking=ranking,
        )
