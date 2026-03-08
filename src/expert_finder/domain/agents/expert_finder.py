"""Core agent logic for expert identification."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TypeAlias
from typing import Any

from expert_finder.domain.ports import LLMPort
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.domain.models import FinalResult, QueryExtractionList

SupportedTool: TypeAlias = EducationSearchTool | WorkExperienceSearchTool
ToolQueriesBySource: TypeAlias = dict[str, QueryExtractionList]
SerializedQuery: TypeAlias = dict[str, Any]
SerializedToolQueries: TypeAlias = dict[str, list[SerializedQuery]]


@dataclass(frozen=True, slots=True)
class ExpertFinderRunOutput:
    result: FinalResult
    metrics: dict[str, int]
    query_parameters: ToolQueriesBySource
    profiles: list[dict[str, Any]]


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
        return self.run_with_metrics(question).result

    def run_with_metrics(
        self, question: str
    ) -> ExpertFinderRunOutput:
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
        query_parameters: ToolQueriesBySource = {
            "education_search": edu_tool_args,
            "professional_search": professional_tool_args,
        }

        candidate_names = list(dict.fromkeys(edu_results + professional_results))
        logger.info("Tool searches returned %s candidates.", len(candidate_names))

        if not candidate_names:
            return ExpertFinderRunOutput(
                result=FinalResult(experts=[]),
                metrics={
                    "education_candidates": len(edu_results),
                    "professional_candidates": len(professional_results),
                    "total_candidates": 0,
                    "profiles_compared": 0,
                },
                query_parameters=query_parameters,
                profiles=[],
            )

        # Compare candidates based on their profiles
        profiles = self.profile_compare.build_profiles(candidate_names)
        # logger.debug("Profiles payload:\n%s", pprint.pformat(profiles, width=100))
        result = self.profile_compare.compare_profiles(
            question,
            profiles,
            self.llm,
            search_context=self._build_search_context(query_parameters),
        )
        profile_by_name = {profile["name"]: profile for profile in profiles}
        enriched_experts = []
        for expert in result.experts:
            enriched_experts.append(
                expert.model_copy(update={"profile": profile_by_name.get(expert.name)})
            )
        result = result.model_copy(update={"experts": enriched_experts})
        logger.info("Expert finder run completed with %s experts.", len(result.experts))
        return ExpertFinderRunOutput(
            result=result,
            metrics={
                "education_candidates": len(edu_results),
                "professional_candidates": len(professional_results),
                "total_candidates": len(candidate_names),
                "profiles_compared": len(profiles),
            },
            query_parameters=query_parameters,
            profiles=profiles,
        )

    def use_search_tool(self, tool: SupportedTool, question: str) -> tuple[list[str], QueryExtractionList]:
        tool_args = tool.build_tool_args(question, self.llm)
        logger = logging.getLogger(self.__class__.__name__)
        logger.debug(
            "Tool %s built args: %s",
            tool.__class__.__name__,
            self._serialize_queries(tool_args),
        )
        results: list[str] = []
        for query in tool_args:
            if not query.tool_required:
                continue
            filter_column = query.filter_column
            filter_value = query.filter_value
            if filter_value and not filter_column:
                if isinstance(tool, EducationSearchTool):
                    filter_column = EducationSearchTool.DEFAULT_FILTER_COLUMN
                if isinstance(tool, WorkExperienceSearchTool):
                    filter_column = WorkExperienceSearchTool.DEFAULT_FILTER_COLUMN
            results.extend(
                tool.search(
                    filter_column=filter_column,
                    filter_value=filter_value,
                    sort_by=query.sort_by,
                    sort_order=query.sort_order,
                    ranking=query.ranking,
                )
            )
        return results, tool_args

    @staticmethod
    def _serialize_queries(queries: QueryExtractionList) -> list[SerializedQuery]:
        """Convert a list of query models to JSON-serializable dictionaries."""
        return [query.model_dump(mode="json") for query in queries]

    def _build_search_context(
        self,
        query_parameters: ToolQueriesBySource,
    ) -> SerializedToolQueries:
        """Build a JSON-serializable search context from extracted tool queries."""
        return {
            tool_name: self._serialize_queries(queries)
            for tool_name, queries in query_parameters.items()
        }
