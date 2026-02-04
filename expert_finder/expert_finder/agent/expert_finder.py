"""Core agent logic for expert identification."""

from __future__ import annotations

import json
import logging
import pprint
from typing import TypeAlias

from expert_finder.expert_finder.llm.ports import LLMPort
from expert_finder.expert_finder.tools.education_search import EducationSearchTool
from expert_finder.expert_finder.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.expert_finder.tools.profile_compare import ProfileComparisonTool
from expert_finder.expert_finder.types.schemas import FinalResult

SupportedTool: TypeAlias = EducationSearchTool | WorkExperienceSearchTool


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

        # Retrieve candidates based on their education
        edu_results = self.use_search_tool(self.education_search, question)
        logger.debug(
            "Education tool returned %d candidates (first up to 5): %s",
            len(edu_results),
            edu_results[:5],
        )

        # Retrieve candidates based on their professional experience
        professional_results = self.use_search_tool(self.professional_search, question)
        logger.debug(
            "Work experience tool returned %d candidates (first up to 5): %s",
            len(professional_results),
            professional_results[:5],
        )

        candidate_names = set(edu_results) | set(professional_results)
        logger.info("Tool searches returned %s candidates.", len(candidate_names))

        if not candidate_names:
            return FinalResult(experts=[])

        # Compare candidates based on their profiles
        profiles = self.profile_compare.build_profiles(candidate_names)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Profiles payload:\n%s", pprint.pformat(profiles, width=100))
        result = self.profile_compare.compare_profiles(
            question,
            profiles,
            self.llm,
        )
        profile_by_name = {profile["name"]: profile for profile in profiles}
        enriched_experts = []
        for expert in result.experts:
            enriched_experts.append(
                expert.model_copy(update={"profile": profile_by_name.get(expert.name)})
            )
        result = result.model_copy(update={"experts": enriched_experts})
        logger.info("Expert finder run completed with %s experts.", len(result.experts))
        return result

    def use_search_tool(self, tool: SupportedTool, question: str) -> list[str]:
        tool_args = tool.build_tool_args(question, self.llm)
        logger = logging.getLogger(self.__class__.__name__)
        logger.debug(
            "Tool %s built args: %s",
            tool.__class__.__name__,
            tool_args.model_dump(mode="json"),
        )
        if tool_args.tool_required and tool_args.institution:
            return tool.search(tool_args.institution)
        return []
