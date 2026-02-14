"""Profile comparison tool for aggregating education and professional records."""

from __future__ import annotations

import json
import logging

from expert_finder.domain.ports import LLMPort
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.domain.models import FinalResult


class ProfileComparisonTool:
    def __init__(self, education_search: EducationSearchTool, professional_search: WorkExperienceSearchTool) -> None:
        self.education_search = education_search
        self.professional_search = professional_search

    def build_profiles(self, names: list[str]) -> list[dict]:
        education_records = self.education_search.get_records(names)
        professional_records = self.professional_search.get_records(names)

        profiles = []
        for name in names:
            education = [
                {key: value for key, value in record.items() if key != "full_name"}
                for record in education_records.get(name, [])
            ]
            professional = [
                {key: value for key, value in record.items() if key != "full_name"}
                for record in professional_records.get(name, [])
            ]
            profiles.append(
                {
                    "name": name,
                    "education": education,
                    "professional": professional,
                }
            )
        return profiles

    def compare_profiles(
        self,
        question: str,
        profiles: list[dict],
        llm: LLMPort,
        search_context: dict | None = None,
    ) -> FinalResult:
        logger = logging.getLogger(self.__class__.__name__)
        system_prompt = (
            "You are an expert comparator. "
            "Given the question, search_context, and profiles (each profile has education and professional lists), "
            "select the top 3 most relevant people. "
            "Primary objective: select people who can help the asker reach the target opportunity "
            "(target role, target lab/company, target program), not people matching the asker's current background. "
            "Disregard personal/background information about the asker unless it directly defines the target "
            "opportunity constraints. "
            "If the question includes both background context and target context, prioritize target context. "
            "Treat conversational terms as non-ranking noise (e.g., coffee chat, advice, help, chiacchierata). "
            "Role disambiguation: treat 'quant' as a job role (quantitative researcher), not generic "
            "quantitative skills. "
            "If an explicit target role is present (e.g., quant, research engineer), prioritize role fit over "
            "generic topical overlap. "
            "Use search_context as a strong prior: inferred filter_column/filter_value, ranking signals, and "
            "sorting intent from education_search and professional_search should guide final relevance decisions. "
            "If search_context is missing or partially empty, fall back to question + profile evidence only. "
            "When dates are available, prefer people with more recent experiences. "
            "If the question implies current or recent enrollment/experience (e.g., 'currently', "
            "'this year', 'recently', 'now', or similar), then: "
            "1) Prefer candidates with missing end_date (assume ongoing), and "
            "2) Prefer candidates whose end_date is within the last 3 years, "
            "3) Downrank candidates whose end_date is older than 3 years unless recall is needed. "
            "If both start_date and end_date are missing, treat the timeframe as unknown and "
            "rank lower than clear current/recent matches. "
            "In each reason, explain the concrete evidence from profile fields (role/company/description/"
            "degree/field_of_study/dates) that supports selection. "
            "Return ONLY valid JSON with key: experts (list). Each expert must have "
            "name (string) and reason (string) explaining why they were selected. "
            "Schema: FinalResult"
        )
        payload = {
            "question": question,
            "search_context": search_context or {},
            "profiles": profiles,
        }
        user_prompt = f"PAYLOAD:\n{json.dumps(payload)}"
        result = llm.call_json(FinalResult, system_prompt, user_prompt)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Final result: %s", result.model_dump(mode="json"))
        return result


def main() -> None:
    tool = ProfileComparisonTool(
        education_search=EducationSearchTool(),
        professional_search=WorkExperienceSearchTool(),
    )
    profiles = tool.build_profiles(["Matteo Oldani"])
    print(json.dumps(profiles, indent=2))


if __name__ == "__main__":
    main()
