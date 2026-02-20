"""Factory helpers for constructing the Expert Finder agent."""

from __future__ import annotations

from expert_finder.config.settings import AgentSettings
from expert_finder.config.settings import ApiSettings
from expert_finder.config.settings import get_api_settings
from expert_finder.config.settings import get_agent_settings
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.ports.llm import LLMPort
from expert_finder.domain.ports.repositories import EducationRepository
from expert_finder.domain.ports.repositories import WorkExperienceRepository
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.infrastructure.llm.adapters.gpt import GPTLLM
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository
from expert_finder.infrastructure.persistence.sqlalchemy.question_logs_repo import SqlAlchemyQuestionLogRepository
from expert_finder.domain.ports.repositories import QuestionLogRepository


def get_llm(
    settings: AgentSettings | None = None,
) -> LLMPort:
    """Construct the default LLMPort implementation."""
    settings = settings or get_agent_settings()
    return GPTLLM(model=settings.gpt_model, temperature=settings.llm_temperature)


def get_education_repository() -> EducationRepository:
    """Construct the default EducationRepository."""
    return CsvEducationRepository()


def get_work_experience_repository() -> WorkExperienceRepository:
    """Construct the default WorkExperienceRepository."""
    return CsvWorkExperienceRepository()


def get_education_search_tool(
    education_repo: EducationRepository | None = None,
) -> EducationSearchTool:
    """Construct the EducationSearchTool."""
    education_repo = education_repo or get_education_repository()
    return EducationSearchTool(education_repo=education_repo)


def get_work_experience_search_tool(
    work_repo: WorkExperienceRepository | None = None,
) -> WorkExperienceSearchTool:
    """Construct the WorkExperienceSearchTool."""
    work_repo = work_repo or get_work_experience_repository()
    return WorkExperienceSearchTool(work_repo=work_repo)


def get_profile_comparison_tool(
    education_search: EducationSearchTool | None = None,
    professional_search: WorkExperienceSearchTool | None = None,
) -> ProfileComparisonTool:
    """Construct the ProfileComparisonTool."""
    education_search = education_search or get_education_search_tool()
    professional_search = professional_search or get_work_experience_search_tool()
    return ProfileComparisonTool(
        education_search=education_search,
        professional_search=professional_search,
    )


def get_agent(
    llm: LLMPort | None = None,
    education_search: EducationSearchTool | None = None,
    professional_search: WorkExperienceSearchTool | None = None,
    profile_compare: ProfileComparisonTool | None = None,
) -> ExpertFinderAgent:
    """Construct the ExpertFinderAgent."""
    llm = llm or get_llm()
    education_search = education_search or get_education_search_tool()
    professional_search = professional_search or get_work_experience_search_tool()
    profile_compare = profile_compare or get_profile_comparison_tool(
        education_search=education_search,
        professional_search=professional_search,
    )
    return ExpertFinderAgent(
        llm=llm,
        education_search=education_search,
        professional_search=professional_search,
        profile_compare=profile_compare,
    )


def get_question_log_repository(
    settings: ApiSettings | None = None,
) -> QuestionLogRepository:
    """Construct the QuestionLogRepository."""
    settings = settings or get_api_settings()
    return SqlAlchemyQuestionLogRepository(db_url=settings.question_logs_db_url)

if __name__ == "__main__":
    # instantiate the agent and test it with a sample question
    agent = get_agent()
    print(agent)
