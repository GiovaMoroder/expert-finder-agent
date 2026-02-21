import json
import re

from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.domain.ports import LLMPort
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository


class _FakeLLM(LLMPort):
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        schema_match = re.search(r"Schema:\s*(\w+)", system_prompt)
        schema_name = schema_match.group(1) if schema_match else ""

        if schema_name == "QueryExtraction":
            return json.dumps(
                {
                    "tool_required": True,
                    "filter_column": "company" if "professional experience" in system_prompt.lower() else "institution",
                    "filter_value": "OpenAI",
                    "sort_by": "start_date",
                    "sort_order": "desc",
                    "ranking": None,
                }
            )

        if schema_name == "FinalResult":
            return json.dumps(
                {
                    "experts": [
                        {
                            "name": "Matteo Oldani",
                            "reason": "Relevant profile match for the target opportunity.",
                        }
                    ]
                }
            )

        raise ValueError(f"Unsupported schema in fake LLM: {schema_name}")


def test_agent_basic_flow():
    education_search = EducationSearchTool(education_repo=CsvEducationRepository())
    professional_search = WorkExperienceSearchTool(work_repo=CsvWorkExperienceRepository())
    agent = ExpertFinderAgent(
        llm=_FakeLLM(),
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
