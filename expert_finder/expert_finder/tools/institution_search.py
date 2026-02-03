"""Professional search tool for CSV data."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from expert_finder.expert_finder.llm.port import LLMPort
from expert_finder.expert_finder.path import PROFESSIONAL_CSV
from expert_finder.expert_finder.types.schemas import QueryExtraction

DEFAULT_COLUMNS = (
    "company",
)


@dataclass(frozen=True)
class ProfessionalSearchTool:
    """Return all members who worked at an institution.

    TODO: Replace with database query and indexing.
    """

    csv_path: Path = PROFESSIONAL_CSV

    _df: pd.DataFrame | None = None

    def _load(self) -> pd.DataFrame:
        logger = logging.getLogger(self.__class__.__name__)
        if self._df is not None:
            return self._df

        if not self.csv_path.exists():
            raise FileNotFoundError(f"Professional CSV not found at {self.csv_path}")

        df = pd.read_csv(self.csv_path)
        for col in DEFAULT_COLUMNS:
            if col in df.columns:
                df[f"_norm_{col}"] = df[col].fillna("").map(_normalize)
            else:
                df[f"_norm_{col}"] = ""

        object.__setattr__(self, "_df", df)
        logger.debug("Loaded professional CSV with %s rows.", len(df))
        return df

    def search(
        self,
        query: str,
        columns: Iterable[str] = DEFAULT_COLUMNS,
        top_k: int = 10,
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

        names = []
        for _, row in results_df.head(top_k).iterrows():
            name = row.get("full_name")
            if not name:
                continue
            names.append(name)

        logger.debug("Professional search for %r returned %s results.", query, len(names))
        return names

    def extract_query(self, question: str, llm: LLMPort) -> QueryExtraction:
        """Extract query parameters from the question for professional search."""

        system_prompt = (
            """
            You are an information extraction assistant.

            Your task is to analyze a user request for finding people in an internal directory
            and extract structured search criteria.

            The directory can be searched by:
            - professional experience (companies, roles, industries, skills), or
            - past education (universities, degrees, academic background).

            DECISION RULES:
            - Set tool_required = true if the user’s request explicitly or implicitly requires
              searching by professional experience (company, job, work history).
            - Set tool_required = false if the search should be based only on education
              and professional experience is not relevant.

            FIELD EXTRACTION RULES:
            - institution:
              - Populate ONLY if tool_required = true.
              - Use the company or organization explicitly mentioned by the user.
              - If professional experience is relevant but no organization is mentioned, set to null.
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


def _normalize(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(text).lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def main() -> None:
    tool = ProfessionalSearchTool()
    for query in ["Google"]:
        print(f"Query: {query}")
        results = tool.search(query, top_k=10)
        unique_names = sorted(set(results))
        df = tool._load()
        if "full_name" in df.columns:
            matches = df[df["full_name"].isin(unique_names)]
            demo_cols = ("full_name", "company", "title", "role", "field_of_work")
            display_cols = [col for col in demo_cols if col in matches.columns]
            if display_cols:
                display_df = (
                    matches[display_cols]
                    .drop_duplicates()
                    .sort_values(by=[col for col in ("full_name", "company") if col in matches.columns], kind="stable")
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
