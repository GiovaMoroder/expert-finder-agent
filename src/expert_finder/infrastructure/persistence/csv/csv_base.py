from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Literal

import pandas as pd
from rapidfuzz import fuzz

from expert_finder.domain.models import RankingRule


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

    def _search_dataframe(
        self,
        df: pd.DataFrame,
        filter_column: str,
        filter_value: str,
        top_k: int,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
        ranking: dict[str, RankingRule] | None = None,
    ) -> list[str]:
        del min_score
        results_df = self._filter_results_dataframe(df, filter_column=filter_column, filter_value=filter_value)
        results_df, ranking_applied = self._rank_results_dataframe(results_df, ranking=ranking)

        if ranking_applied:
            results_df = results_df.head(top_k)

        results_df = self._sort_results_dataframe(results_df, sort_by=sort_by, sort_order=sort_order)

        results_df = self._sort_results_dataframe(results_df, sort_by=sort_by, sort_order=sort_order)

        names: list[str] = []
        rows = results_df.iterrows() if ranking_applied else results_df.head(top_k).iterrows()
        for _, row in rows:
            name = row.get("full_name")
            if name:
                names.append(name)
        return names

    def _filter_results_dataframe(self, df: pd.DataFrame, filter_column: str, filter_value: str) -> pd.DataFrame:
        logger = logging.getLogger(self.__class__.__name__)

        if filter_column not in df.columns:
            logger.warning("Invalid filter column '%s'. Available columns: %s", filter_column, list(df.columns))
            return df

        normalized_filter = self._normalize(filter_value)
        if not normalized_filter:
            logger.warning("Empty filter value for filter column '%s'. Skipping filtering.", filter_column)
            return df

        normalized_series = df[filter_column].fillna("").map(self._normalize)
        mask = normalized_series.str.contains(normalized_filter, na=False)
        return df[mask]

    def _rank_results_dataframe(
        self,
        results_df: pd.DataFrame,
        ranking: dict[str, RankingRule] | None,
    ) -> tuple[pd.DataFrame, bool]:
        if not ranking:
            return results_df, False

        logger = logging.getLogger(self.__class__.__name__)
        valid_rules: list[tuple[str, RankingRule]] = []
        for column, rule in ranking.items():
            if column not in results_df.columns:
                logger.warning(
                    "Invalid ranking column '%s'. Available columns: %s", column, list(results_df.columns)
                )
                continue
            keyword = rule.keyword.strip()
            if not keyword:
                logger.warning("Ranking keyword for column '%s' is empty. Ignoring this ranking rule.", column)
                continue
            if rule.weight <= 0:
                logger.warning("Ranking weight for column '%s' must be > 0. Ignoring this ranking rule.", column)
                continue
            valid_rules.append((column, rule))

        if not valid_rules:
            return results_df, False

        total_weight = sum(rule.weight for _, rule in valid_rules)
        if total_weight <= 0:
            logger.warning("Total ranking weight is <= 0. Skipping ranking.")
            return results_df, False

        normalized_rules = [(column, rule.weight / total_weight, rule.keyword) for column, rule in valid_rules]

        ranked_df = results_df.copy()

        def row_score(row: pd.Series) -> float:
            score = 0.0
            for column, normalized_weight, keyword in normalized_rules:
                cell_value = row.get(column, "")
                similarity = fuzz.token_set_ratio(str(cell_value or ""), keyword) / 100.0
                score += normalized_weight * similarity
            return score

        ranked_df["_ranking_score"] = ranked_df.apply(row_score, axis=1)
        ranked_df = ranked_df.sort_values(by="_ranking_score", ascending=False, kind="stable")
        return ranked_df.drop(columns=["_ranking_score"]), True

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
