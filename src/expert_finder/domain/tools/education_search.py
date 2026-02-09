"""Education search tool backed by repository."""

from __future__ import annotations

from expert_finder.domain.education_normalization import normalize_school
from expert_finder.domain.ports import EducationRepository
from expert_finder.domain.ports import LLMPort
from expert_finder.domain.models import QueryExtraction


class EducationSearchTool:
    """Search education data with fuzzy matching."""

    def __init__(self, education_repo: EducationRepository | None = None) -> None:
        self.education_repo = education_repo

    def search(self, query: str, top_k: int = 10, min_score: float = 0.0) -> list[str]:
        normalized_query = normalize_school(query)
        if normalized_query is None:
            return []
        return self.education_repo.search(normalized_query, top_k=top_k, min_score=min_score)

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

            Schema: QueryExtraction
            """
        )
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
        results = tool.search(query, top_k=10, min_score=0.5)
        unique_names = sorted(set(results))
        if unique_names:
            records = tool.get_records(unique_names)
            for name in unique_names:
                print(name, records.get(name, []))
        print("-" * 40)
