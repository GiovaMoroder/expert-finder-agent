"""Factory helpers for constructing the Expert Finder agent."""

from __future__ import annotations

from expert_finder.config.settings import AgentSettingsProvider
from expert_finder.config.settings import get_agent_settings
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.infrastructure.llm.adapters.stub import DeterministicStubLLM
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository


def build_agent(
    *,
    settings_provider: AgentSettingsProvider = get_agent_settings,
    use_stub_llm: bool = False,
) -> ExpertFinderAgent:
    """Construct the default Expert Finder agent."""
    settings = settings_provider()

    education_search = EducationSearchTool(education_repo=CsvEducationRepository())
    professional_search = WorkExperienceSearchTool(work_repo=CsvWorkExperienceRepository())
    if use_stub_llm:
        llm = DeterministicStubLLM()
    else:
        from expert_finder.infrastructure.llm.adapters.gpt import GPTLLM

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
