"""Core agent logic for expert identification."""

from __future__ import annotations

import json
import logging
import pprint
from typing import TypeAlias
from typing import Any

from expert_finder.domain.ports import LLMPort
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.domain.models import FinalResult, QueryExtraction

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
        result, _, _ = self.run_with_metrics(question)
        return result

    def run_with_metrics(
        self, question: str
    ) -> tuple[FinalResult, dict[str, int], dict[str, dict[str, Any]]]:
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Starting expert finder run.")
        logger.debug("Question: %s", question)

        # Retrieve candidates based on their education
        edu_results, edu_tool_args = self.use_search_tool(self.education_search, question)
        logger.debug(
            "Education tool returned %d candidates (first up to 5)",
            len(edu_results)
            # edu_results[:5],
        )

        # Retrieve candidates based on their professional experience
        professional_results, professional_tool_args = self.use_search_tool(self.professional_search, question)
        logger.debug(
            "Work experience tool returned %d candidates (first up to 5)",
            len(professional_results)
            # professional_results[:5],
        )
        query_parameters = {
            "education_search": edu_tool_args.model_dump(mode="json"),
            "professional_search": professional_tool_args.model_dump(mode="json"),
        }

        candidate_names = set(edu_results) | set(professional_results)
        logger.info("Tool searches returned %s candidates.", len(candidate_names))

        if not candidate_names:
            return FinalResult(experts=[]), {
                "education_candidates": len(edu_results),
                "professional_candidates": len(professional_results),
                "total_candidates": 0,
                "profiles_compared": 0,
            }, query_parameters

        # Compare candidates based on their profiles
        profiles = self.profile_compare.build_profiles(candidate_names)
        # logger.debug("Profiles payload:\n%s", pprint.pformat(profiles, width=100))
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
        return result, {
            "education_candidates": len(edu_results),
            "professional_candidates": len(professional_results),
            "total_candidates": len(candidate_names),
            "profiles_compared": len(profiles),
        }, query_parameters

    def use_search_tool(self, tool: SupportedTool, question: str) -> tuple[list[str], QueryExtraction]:
        tool_args = tool.build_tool_args(question, self.llm)
        logger = logging.getLogger(self.__class__.__name__)
        logger.debug(
            "Tool %s built args: %s",
            tool.__class__.__name__,
            tool_args.model_dump(mode="json"),
        )
        if tool_args.tool_required:
            filter_column = tool_args.filter_column
            filter_value = tool_args.filter_value
            if isinstance(tool, EducationSearchTool):
                filter_column = filter_column or EducationSearchTool.DEFAULT_FILTER_COLUMN
            if isinstance(tool, WorkExperienceSearchTool):
                filter_column = filter_column or WorkExperienceSearchTool.DEFAULT_FILTER_COLUMN
            if not filter_column or not filter_value:
                return [], tool_args
            return tool.search(
                filter_column=filter_column,
                filter_value=filter_value,
                sort_by=tool_args.sort_by,
                sort_order=tool_args.sort_order,
                ranking=tool_args.ranking,
            ), tool_args
        return [], tool_args
