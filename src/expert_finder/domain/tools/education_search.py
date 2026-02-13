"""Education search tool backed by repository."""

from __future__ import annotations

from dataclasses import fields
from typing import Literal

from expert_finder.domain.education_normalization import normalize_school
from expert_finder.domain.models import EducationRecord, RankingRule
from expert_finder.domain.ports import EducationRepository
from expert_finder.domain.ports import LLMPort
from expert_finder.domain.models import QueryExtraction


class EducationSearchTool:
    """Search education data with fuzzy matching."""

    AVAILABLE_COLUMNS = tuple(field.name for field in fields(EducationRecord))
    DEFAULT_FILTER_COLUMN = "institution"

    def __init__(self, education_repo: EducationRepository | None = None) -> None:
        self.education_repo = education_repo

    def search(
        self,
        filter_column: str,
        filter_value: str,
        top_k: int = 10,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
        ranking: dict[str, RankingRule] | None = None,
    ) -> list[str]:
        normalized_query = normalize_school(filter_value)
        if normalized_query is None:
            return []
        return self.education_repo.search(
            filter_column=filter_column,
            filter_value=normalized_query,
            top_k=top_k,
            min_score=min_score,
            sort_by=sort_by,
            sort_order=sort_order,
            ranking=ranking,
        )

    # TODO: consider using sorting by date as a default in the tool
    def build_tool_args(self, question: str, llm: LLMPort) -> QueryExtraction:
        """Build tool arguments from the question for education search."""

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

            OBJECTIVE RULE:
            - The objective is to find people who can help the asker reach their target opportunity.
            - Prioritize the target institution/opportunity context over the asker's background context.

            FILTER RULES:
            - Allowed columns are: __AVAILABLE_COLUMNS__.
            - Pick exactly one filter_column and one filter_value when tool_required = true.
            - Prefer filter_column = "__DEFAULT_FILTER_COLUMN__" unless the user clearly asks for another column.
            - Strong rule: if the user mentions a school/university/institution, use it as filter_value and set
              filter_column = "__DEFAULT_FILTER_COLUMN__" unless the user explicitly asks another column.
            - If multiple institutions are mentioned, choose the one linked to the desired position/interview/
              application/lab where help is requested, not the one describing the asker's current affiliation.
            - If tool_required = false, set filter_column = null and filter_value = null.
            
            SORTING RULES:
            - Allowed sortable columns for education are: __AVAILABLE_COLUMNS__.
            - Infer sorting from context, even when user does not explicitly say "sort by".
            - If the user asks for recency/current/latest/recently, set sort_by = "start_date" and sort_order = "desc".
            - If the user asks for oldest/earliest/first, set sort_by = "start_date" and sort_order = "asc".
            - If the user explicitly asks for a specific sortable column, use it exactly.
            - Never invent field names.
            - Default behavior: if no sorting intent is present, set sort_by = "start_date" and sort_order = "desc".

            RANKING RULES:
            - ranking is optional, but strongly recommended whenever it can improve relevance.
            - Good ranking candidates include degree type/name and field signals:
              - degree
              - field_of_study
            - ranking must be a JSON object keyed by column name, with value:
              {"weight": number, "keyword": string}
            - Use only allowed columns as ranking keys.
            - Weights are non-negative and will be normalized later.
            - Example:
              {
                "field_of_study": {"weight": 0.6, "keyword": "data science"},
                "degree": {"weight": 0.4, "keyword": "master"}
              }

            OUTPUT CONSTRAINTS:
            - Return ONLY valid JSON.
            - Do NOT include explanations, comments, or extra text.
            - Use exactly the following schema:
            
            {
              "tool_required": boolean,
              "filter_column": string | null,
              "filter_value": string | null,
              "sort_by": string | null,
              "sort_order": "asc" | "desc" | null,
              "ranking": { "<column_name>": { "weight": number, "keyword": string } } | null
            }

            Schema: QueryExtraction
            """
        )
        system_prompt = system_prompt.replace("__AVAILABLE_COLUMNS__", ", ".join(self.AVAILABLE_COLUMNS))
        system_prompt = system_prompt.replace("__DEFAULT_FILTER_COLUMN__", self.DEFAULT_FILTER_COLUMN)
        user_prompt = question
        extraction = llm.call_json(QueryExtraction, system_prompt, user_prompt)
        return extraction

    def get_records(self, names: list[str]) -> dict[str, list[dict]]:
        records_by_name: dict[str, list[dict]] = {name: [] for name in names}
        for record in self.education_repo.list_all():
            if record.full_name in records_by_name:
                records_by_name[record.full_name].append(record.__dict__)
        return records_by_name


if __name__ == "__main__":
    tool = EducationSearchTool()
    for query in ("epfl", "Trieste"):
        print(f"Query: {query}")
        results = tool.search("institution", query, top_k=10, min_score=0.5)
        unique_names = sorted(set(results))
        if unique_names:
            records = tool.get_records(unique_names)
            for name in unique_names:
                print(name, records.get(name, []))
        print("-" * 40)
