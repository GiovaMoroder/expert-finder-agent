"""Core agent logic for expert identification."""

from __future__ import annotations

import json
import logging

from expert_finder.expert_finder.llm.ports import LLMPort
from expert_finder.expert_finder.tools.education_search import EducationSearchTool
from expert_finder.expert_finder.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.expert_finder.tools.profile_compare import ProfileComparisonTool
from expert_finder.expert_finder.types.schemas import FinalResult


class ExpertFinderAgent:
    def __init__(
        self,
        llm: LLMPort,
        education_search: EducationSearchTool,
        professional_search: WorkExperienceSearchTool,
        profile_compare: ProfileComparisonTool,
    ) -> None:
        self.llm = llm
        self.education_search = education_search
        self.professional_search = professional_search
        self.profile_compare = profile_compare

    def run(self, question: str) -> FinalResult:
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Starting expert finder run.")
        logger.debug("Question: %s", question)

        education_extraction = self.education_search.extract_query(question, self.llm)
        professional_extraction = self.professional_search.extract_query(question, self.llm)
        logger.info(
            "Extraction result (education): %s", education_extraction.model_dump(mode="json")
        )
        logger.info(
            "Extraction result (professional): %s",
            professional_extraction.model_dump(mode="json"),
        )

        candidate_names: set[str] = set()
        if education_extraction.tool_required and education_extraction.institution:
            candidate_names.update(
                self.education_search.search(education_extraction.institution)
            )
        if professional_extraction.tool_required and professional_extraction.institution:
            candidate_names.update(
                self.professional_search.search(professional_extraction.institution)
            )

        candidates = sorted(candidate_names)[:7]
        logger.info("Tool searches returned %s candidates.", len(candidates))
        if not candidates:
            return FinalResult(experts=[])

        profiles = self.profile_compare.build_profiles(candidates)
        result = self.profile_compare.compare_profiles(
            question,
            {
                "education": education_extraction.model_dump(mode="json"),
                "professional": professional_extraction.model_dump(mode="json"),
            },
            profiles,
            self.llm,
        )
        logger.info("Expert finder run completed with %s experts.", len(result.experts))
        return result
