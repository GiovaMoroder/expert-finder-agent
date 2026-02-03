"""Education search tool for CSV data."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from expert_finder.expert_finder.llm.port import LLMPort
from expert_finder.expert_finder.path import EDUCATION_CSV
from expert_finder.expert_finder.types.schemas import QueryExtraction

DEFAULT_COLUMNS = (
    "full_name",
    "school",
    "field_of_study",
    "degree",
    "degree_name",
)


def _normalize(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(text).lower())
    return re.sub(r"\s+", " ", cleaned).strip()


@dataclass(frozen=True)
class EducationSearchTool:
    """Search education CSV with fuzzy matching."""

    csv_path: Path = EDUCATION_CSV

    _df: pd.DataFrame | None = None

    def _load(self) -> pd.DataFrame:
        logger = logging.getLogger(self.__class__.__name__)
        if self._df is not None:
            return self._df

        if not self.csv_path.exists():
            raise FileNotFoundError(f"Education CSV not found at {self.csv_path}")

        df = pd.read_csv(self.csv_path)
        for col in DEFAULT_COLUMNS:
            if col in df.columns:
                df[f"_norm_{col}"] = df[col].fillna("").map(_normalize)
            else:
                df[f"_norm_{col}"] = ""

        object.__setattr__(self, "_df", df)
        logger.debug("Loaded education CSV with %s rows.", len(df))
        return df

    def search(
        self,
        query: str,
        columns: Iterable[str] = DEFAULT_COLUMNS,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[str]:
        logger = logging.getLogger(self.__class__.__name__)
        df = self._load()
        normalized_query = _normalize(query)
        if not normalized_query:
            return []

        norm_columns = [f"_norm_{col}" for col in columns]
        mask = False
        for col in norm_columns:
            mask |= df[col].str.contains(normalized_query, na=False)

        results_df = df[mask]

        if min_score > 0.0 and len(results_df) > 0:
            scores = []
            for _, row in results_df.iterrows():
                texts = [row.get(col, "") for col in norm_columns]
                score = 1.0 if any(normalized_query in text for text in texts) else 0.0
                if score >= min_score:
                    record = {col: row.get(col) for col in DEFAULT_COLUMNS if col in df.columns}
                    record["score"] = round(score, 3)
                    scores.append(record)
            raw_results = scores[:top_k]
        else:
            raw_results = [
                {col: row.get(col) for col in DEFAULT_COLUMNS if col in df.columns}
                for _, row in results_df.head(top_k).iterrows()
            ]

        names = []
        for record in raw_results:
            name = record.get("full_name")
            if not name:
                continue
            names.append(name)

        logger.debug("Education search for %r returned %s results.", query, len(names))
        return names

    def extract_query(self, question: str, llm: LLMPort) -> QueryExtraction:
        """Extract query parameters from the question for education search."""

        system_prompt = (
            """
            You are an information extraction assistant.

            Your task is to analyze a user request for finding people in an internal directory
            and extract structured search criteria.
            
            The directory can be searched by:
            - past education (university, degree, master, PhD, or similar), or
            - professional experience (roles, jobs, industries, skills).
            
            DECISION RULES:
            - Set tool_required = true if the user’s request explicitly or implicitly requires
              searching by past education (e.g. university attended, degree obtained, academic background).
            - Set tool_required = false if the search should be based only on professional experience
              or current role, and education is not relevant.
            
            FIELD EXTRACTION RULES:
            - institution:
              - Populate ONLY if tool_required = true.
              - Use the school or university explicitly mentioned by the user.
              - If education is relevant but no institution is mentioned, set to null.
            - role:
              - Populate with a professional role or title if mentioned (e.g. "data scientist").
              - Otherwise, set to null.
            - topic:
              - Populate with a subject area, field, or expertise the user is interested in
                (e.g. "reinforcement learning", "econometrics").
              - Otherwise, set to null.
            
            OUTPUT CONSTRAINTS:
            - Return ONLY valid JSON.
            - Do NOT include explanations, comments, or extra text.
            - Use exactly the following schema:
            
            {
              "tool_required": boolean,
              "institution": string | null,
              "role": string | null,
              "topic": string | null
            }
            """
        )
        user_prompt = question
        extraction = llm.call_json(QueryExtraction, system_prompt, user_prompt)
        return extraction

    def get_records(self, names: list[str]) -> dict[str, list[dict]]:
        df = self._load()
        if "full_name" not in df.columns:
            return {name: [] for name in names}

        matches = df[df["full_name"].isin(names)]
        columns = [col for col in df.columns if not col.startswith("_norm_")]
        records_by_name: dict[str, list[dict]] = {name: [] for name in names}
        for _, row in matches.iterrows():
            name = row.get("full_name")
            if not name:
                continue
            record = {col: row.get(col) for col in columns}
            records_by_name.setdefault(name, []).append(record)
        return records_by_name


def main() -> None:
    tool = EducationSearchTool()
    for query in ("epfl", "Trieste"):
        print(f"Query: {query}")
        results = tool.search(query, top_k=10, min_score=0.5)
        unique_names = sorted(set(results))
        df = tool._load()
        if "full_name" in df.columns:
            matches = df[df["full_name"].isin(unique_names)]
            demo_cols = ("full_name", "school", "degree_name", "degree")
            display_cols = [col for col in demo_cols if col in matches.columns]
            if display_cols:
                display_df = (
                    matches[display_cols]
                    .drop_duplicates()
                    .sort_values(by=[col for col in ("full_name", "school") if col in matches.columns], kind="stable")
                )
                print(display_df.to_string(index=False))
            else:
                for _, row in matches.iterrows():
                    print(row.to_dict())
        else:
            for result in unique_names:
                print(result)
        print("-" * 40)


if __name__ == "__main__":
    main()
