from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.infrastructure.llm.adapters.stub import DeterministicStubLLM
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository


def test_agent_basic_flow():
    education_search = EducationSearchTool(education_repo=CsvEducationRepository())
    professional_search = WorkExperienceSearchTool(work_repo=CsvWorkExperienceRepository())
    agent = ExpertFinderAgent(
        llm=DeterministicStubLLM(),
        education_search=education_search,
        professional_search=professional_search,
        profile_compare=ProfileComparisonTool(
            education_search=education_search,
            professional_search=professional_search,
        ),
    )

    result = agent.run("People with previous experience at OpenAI in role Research Engineer")

    assert result.experts
    assert len(result.experts) <= 3
