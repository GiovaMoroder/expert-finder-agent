"""Work experience search tool backed by repository."""

from __future__ import annotations

from dataclasses import fields
from typing import Literal

from expert_finder.domain.models import RankingRule, WorkExperienceRecord
from expert_finder.domain.ports import WorkExperienceRepository
from expert_finder.domain.ports import LLMPort
from expert_finder.domain.models import QueryExtraction


class WorkExperienceSearchTool:
    """Return all members who worked at an institution."""

    AVAILABLE_COLUMNS = tuple(field.name for field in fields(WorkExperienceRecord))
    DEFAULT_FILTER_COLUMN = "company"

    def __init__(self, work_repo: WorkExperienceRepository | None = None) -> None:
        self.work_repo = work_repo

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
        return self.work_repo.search(
            filter_column=filter_column,
            filter_value=filter_value,
            top_k=top_k,
            min_score=min_score,
            sort_by=sort_by,
            sort_order=sort_order,
            ranking=ranking,
        )

    def build_tool_args(self, question: str, llm: LLMPort) -> QueryExtraction:
        """Build tool arguments from the question for professional search."""

        system_prompt_template = (
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

            OBJECTIVE RULE:
            - The objective is to find people who can help the asker reach their target opportunity.
            - Prioritize the target institution/opportunity context over the asker's background context.
            - Role disambiguation: treat "quant" as a job role (quantitative researcher), not generic
              quantitative skills. Never use "quant" in search or ranking, use "quantitative researcher" instead.

            FILTER RULES:
            - Allowed columns are: {available_columns}.
            - Filtering is optional.
            - Set filter_column and filter_value only when a target institution/company is explicitly present.
            - Prefer filter_column = "{default_filter_column}" unless the user clearly asks for another column.
            - Strong rule: if the user mentions an institution/company/organization, use it as filter_value and set
              filter_column = "{default_filter_column}" unless the user explicitly asks another column.
            - If multiple institutions are mentioned, choose the one linked to the desired position/interview/
              application/lab where help is requested, not the one describing the asker's current affiliation.
            - If no target institution/company is mentioned, set filter_column = null and filter_value = null.
            - If tool_required = false, set filter_column = null and filter_value = null.

            SORTING RULES:
            - Allowed sortable columns for work experience are: {available_columns}.
            - Infer sorting from context, even when user does not explicitly say "sort by".
            - If the user asks for recency/current/latest/recently, set sort_by = "start_date" and sort_order = "desc".
            - If the user asks for oldest/earliest/first, set sort_by = "start_date" and sort_order = "asc".
            - If the user explicitly asks for a specific sortable column, use it exactly.
            - Never invent field names.
            - Default behavior: if no sorting intent is present, set sort_by = "start_date" and sort_order = "desc".

            RANKING RULES:
            - ranking is optional, but strongly recommended whenever it can improve relevance.
            - Good ranking candidates include role/title and related profile signals:
              - role
              - description
              - company
            - If the user explicitly asks for a person type/role (e.g., "quant", "research engineer"),
              prioritize role matching and use ranking on "role"
            - In that case, set keyword to the target role term (e.g., "quant"), not to contextual chatter.
            - Do NOT use conversational/support terms as ranking keywords (e.g., "coffee chat", "advice",
              "help", "chiacchierata").
            - Do NOT use first-person background details as ranking keywords unless explicitly requested as
              target criteria
            - ranking must be a JSON object keyed by column name, with value:
              {{"weight": number, "keyword": string}}
            - Use only allowed columns as ranking keys.
            - Weights are non-negative and will be normalized later.
            - Example:
              {{
                "role": {{"weight": 0.7, "keyword": "research engineer"}},
                "description": {{"weight": 0.3, "keyword": "LLM"}}
              }}

            OUTPUT CONSTRAINTS:
            - Return ONLY valid JSON.
            - Do NOT include explanations, comments, or extra text.
            - Use exactly the following schema:

            {{
              "tool_required": boolean,
              "filter_column": string | null,
              "filter_value": string | null,
              "sort_by": string | null,
              "sort_order": "asc" | "desc" | null,
              "ranking": {{ "<column_name>": {{ "weight": number, "keyword": string }} }} | null
            }}

            Schema: QueryExtraction
            """
        )
        system_prompt = system_prompt_template.format(
            available_columns=", ".join(self.AVAILABLE_COLUMNS),
            default_filter_column=self.DEFAULT_FILTER_COLUMN,
        )
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
        results = tool.search("company", query, top_k=10)
        unique_names = sorted(set(results))
        if unique_names:
            records = tool.get_records(unique_names)
            for name in unique_names:
                print(name, records.get(name, []))
        print("-" * 40)
