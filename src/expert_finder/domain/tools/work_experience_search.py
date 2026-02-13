"""Work experience search tool backed by repository."""

from __future__ import annotations

from dataclasses import fields
from typing import Literal

from expert_finder.domain.models import WorkExperienceRecord
from expert_finder.domain.ports import WorkExperienceRepository
from expert_finder.domain.ports import LLMPort
from expert_finder.domain.models import QueryExtraction


class WorkExperienceSearchTool:
    """Return all members who worked at an institution."""

    SORTABLE_COLUMNS = tuple(field.name for field in fields(WorkExperienceRecord))

    def __init__(self, work_repo: WorkExperienceRepository | None = None) -> None:
        self.work_repo = work_repo

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> list[str]:
        return self.work_repo.search(
            query,
            top_k=top_k,
            min_score=min_score,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def build_tool_args(self, question: str, llm: LLMPort) -> QueryExtraction:
        """Build tool arguments from the question for professional search."""

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

            SORTING RULES:
            - Allowed sortable columns for work experience are: __SORTABLE_COLUMNS__.
            - Infer sorting from context, even when user does not explicitly say "sort by".
            - If the user asks for recency/current/latest/recently, set sort_by = "start_date" and sort_order = "desc".
            - If the user asks for oldest/earliest/first, set sort_by = "start_date" and sort_order = "asc".
            - If the user explicitly asks for a specific sortable column, use it exactly.
            - Never invent field names.
            - Default behavior: if no sorting intent is present, set sort_by = "start_date" and sort_order = "desc".

            OUTPUT CONSTRAINTS:
            - Return ONLY valid JSON.
            - Do NOT include explanations, comments, or extra text.
            - Use exactly the following schema:

            {
              "tool_required": boolean,
              "institution": string | null,
              "role": string | null,
              "topic": string | null,
              "sort_by": string | null,
              "sort_order": "asc" | "desc" | null
            }

            Schema: QueryExtraction
            """
        )
        system_prompt = system_prompt.replace("__SORTABLE_COLUMNS__", ", ".join(self.SORTABLE_COLUMNS))
        user_prompt = question
        extraction = llm.call_json(QueryExtraction, system_prompt, user_prompt)
        return extraction

    def get_records(self, names: list[str]) -> dict[str, list[dict]]:
        records_by_name: dict[str, list[dict]] = {name: [] for name in names}
        for record in self.work_repo.list_all():
            if record.full_name in records_by_name:
                records_by_name[record.full_name].append(record.__dict__)
        return records_by_name


if __name__ == "__main__":
    tool = WorkExperienceSearchTool()
    for query in ["Google"]:
        print(f"Query: {query}")
        results = tool.search(query, top_k=10)
        unique_names = sorted(set(results))
        if unique_names:
            records = tool.get_records(unique_names)
            for name in unique_names:
                print(name, records.get(name, []))
        print("-" * 40)
