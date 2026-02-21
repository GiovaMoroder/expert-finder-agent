"""Factory helpers for constructing the Expert Finder agent."""

from __future__ import annotations

import os

from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.infrastructure.config import SETTINGS
from expert_finder.infrastructure.llm.adapters.gpt import GPTLLM
from expert_finder.infrastructure.llm.adapters.stub import DeterministicStubLLM
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository


def build_agent() -> ExpertFinderAgent:
    """Construct the default Expert Finder agent."""
    education_search = EducationSearchTool(education_repo=CsvEducationRepository())
    professional_search = WorkExperienceSearchTool(work_repo=CsvWorkExperienceRepository())
    use_stub = os.environ.get("EXPERT_FINDER_USE_STUB_LLM", "").lower() in {"1", "true", "yes"}
    llm = DeterministicStubLLM() if use_stub else GPTLLM(model=SETTINGS.gpt_model)
    return ExpertFinderAgent(
        llm=llm,
        education_search=education_search,
        professional_search=professional_search,
        profile_compare=ProfileComparisonTool(
            education_search=education_search,
            professional_search=professional_search,
        ),
    )

