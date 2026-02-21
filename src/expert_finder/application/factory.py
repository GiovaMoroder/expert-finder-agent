"""Factory helpers for constructing the Expert Finder agent."""

from __future__ import annotations

import logging

from expert_finder.config.settings import AgentSettingsProvider
from expert_finder.config.settings import get_agent_settings
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.infrastructure.llm.adapters.gpt import GPTLLM
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository


def build_agent(
    *,
    settings_provider: AgentSettingsProvider = get_agent_settings,
) -> ExpertFinderAgent:
    """Construct the default Expert Finder agent."""
    logger = logging.getLogger(__name__)
    settings = settings_provider()
    logger.info("Building ExpertFinderAgent with model=%s", settings.gpt_model)

    education_search = EducationSearchTool(education_repo=CsvEducationRepository())
    professional_search = WorkExperienceSearchTool(work_repo=CsvWorkExperienceRepository())

    llm = GPTLLM(model=settings.gpt_model)
    return ExpertFinderAgent(
        llm=llm,
        education_search=education_search,
        professional_search=professional_search,
        profile_compare=ProfileComparisonTool(
            education_search=education_search,
            professional_search=professional_search,
        ),
    )
