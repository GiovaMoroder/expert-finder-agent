"""Profile comparison tool for aggregating education and professional records."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from expert_finder.expert_finder.llm.port import LLMPort
from expert_finder.expert_finder.tools.education_search import EducationSearchTool
from expert_finder.expert_finder.tools.institution_search import ProfessionalSearchTool
from expert_finder.expert_finder.types.schemas import FinalResult


@dataclass(frozen=True)
class ProfileComparisonTool:
    education_search: EducationSearchTool
    professional_search: ProfessionalSearchTool

    def build_profiles(self, names: list[str]) -> list[dict]:
        education_records = self.education_search.get_records(names)
        professional_records = self.professional_search.get_records(names)

        profiles = []
        for name in names:
            experiences: list[dict] = []
            for record in education_records.get(name, []):
                experiences.append({"type": "education", "data": record})
            for record in professional_records.get(name, []):
                experiences.append({"type": "professional", "data": record})
            profiles.append({"name": name, "experiences": experiences})
        return profiles

    def compare_profiles(self, question: str, extraction: dict, profiles: list[dict], llm: LLMPort) -> FinalResult:
        logger = logging.getLogger(self.__class__.__name__)
        system_prompt = (
            "You are an expert comparator. "
            "Given the question and profiles, select the top 3 most relevant people. "
            "Return ONLY valid JSON with key: experts (list). Each expert must have "
            "name (string) and reason (string) explaining why they were selected. "
            "Schema: FinalResult"
        )
        payload = {
            "question": question,
            "extraction": extraction,
            "profiles": profiles,
        }
        user_prompt = f"PAYLOAD:\n{json.dumps(payload)}"
        result = llm.call_json(FinalResult, system_prompt, user_prompt)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Final result: %s", result.model_dump(mode="json"))
        return result
