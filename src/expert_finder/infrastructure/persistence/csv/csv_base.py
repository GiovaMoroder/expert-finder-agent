from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable
from typing import Literal

import pandas as pd


class CsvRepositoryBase:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path
        self._df: pd.DataFrame | None = None

    def _load(self) -> pd.DataFrame:
        if self._df is None:
            self._df = pd.read_csv(self.csv_path)
        return self._df

    @staticmethod
    def _normalize(text: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", " ", str(text).lower())
        return re.sub(r"\s+", " ", cleaned).strip()

    def _apply_norm_columns(self, df: pd.DataFrame, columns: Iterable[str]) -> None:
        for col in columns:
            if col in df.columns:
                df[f"_norm_{col}"] = df[col].fillna("").map(self._normalize)
            else:
                df[f"_norm_{col}"] = ""

    def _search_dataframe(
        self,
        df: pd.DataFrame,
        query: str,
        columns: Iterable[str],
        top_k: int,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> list[str]:
        normalized_query = self._normalize(query)
        if not normalized_query:
            return []

        norm_columns = [f"_norm_{col}" for col in columns]
        mask = False
        for col in norm_columns:
            if col in df.columns:
                mask |= df[col].str.contains(normalized_query, na=False)

        results_df = df[mask]

        if min_score > 0.0 and len(results_df) > 0:
            scores = []
            for _, row in results_df.iterrows():
                texts = [row.get(col, "") for col in norm_columns]
                score = 1.0 if any(normalized_query in text for text in texts) else 0.0
                if score >= min_score:
                    scores.append(row)
            results_df = pd.DataFrame(scores)

        results_df = self._sort_results_dataframe(results_df, sort_by=sort_by, sort_order=sort_order)

        names: list[str] = []
        for _, row in results_df.head(top_k).iterrows():
            name = row.get("full_name")
            if name:
                names.append(name)
        return names

    def _sort_results_dataframe(
        self,
        results_df: pd.DataFrame,
        sort_by: str | None,
        sort_order: Literal["asc", "desc"] | None,
    ) -> pd.DataFrame:
        if sort_by is None and sort_order is None:
            return results_df

        logger = logging.getLogger(self.__class__.__name__)
        if sort_by is None or sort_order is None:
            logger.warning("Invalid sorting arguments: sort_by=%s sort_order=%s", sort_by, sort_order)
            return results_df
        if sort_by not in results_df.columns:
            logger.warning("Invalid sort column '%s'. Available columns: %s", sort_by, list(results_df.columns))
            return results_df
        if sort_order not in {"asc", "desc"}:
            logger.warning("Invalid sort order '%s'. Expected 'asc' or 'desc'.", sort_order)
            return results_df

        return results_df.sort_values(
            by=sort_by,
            ascending=(sort_order == "asc"),
            na_position="last",
            kind="stable",
        )
