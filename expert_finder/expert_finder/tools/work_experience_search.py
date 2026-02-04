"""Work experience search tool backed by repository."""

from __future__ import annotations

from expert_finder.expert_finder.db.adapters.csv.work_experience_repo import CsvWorkExperienceRepository
from expert_finder.expert_finder.db.ports import WorkExperienceRepository
from expert_finder.expert_finder.llm.ports import LLMPort
from expert_finder.expert_finder.types.schemas import QueryExtraction


class WorkExperienceSearchTool:
    """Return all members who worked at an institution."""

    def __init__(self, work_repo: WorkExperienceRepository | None = None) -> None:
        self.work_repo = work_repo or CsvWorkExperienceRepository()

    def search(self, query: str, top_k: int = 10) -> list[str]:
        return self.work_repo.search(query, top_k=top_k)

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
