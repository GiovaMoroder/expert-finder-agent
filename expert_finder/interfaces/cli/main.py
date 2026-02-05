"""CLI entrypoint for the Expert Finder POC."""

from __future__ import annotations

import argparse
import json
import os

from expert_finder.application.expert_finder.use_case import ExpertFinderAgent
from expert_finder.infrastructure.config import SETTINGS
from expert_finder.infrastructure.llm.adapters.gpt import GPTLLM
from expert_finder.infrastructure.llm.adapters.stub import DeterministicStubLLM
from expert_finder.infrastructure.logging import setup_logging, silence_third_party_loggers
from expert_finder.application.expert_finder.tools.education_search import EducationSearchTool
from expert_finder.application.expert_finder.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.application.expert_finder.tools.profile_compare import ProfileComparisonTool
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository


def build_agent() -> ExpertFinderAgent:
    education_search = EducationSearchTool(education_repo=CsvEducationRepository())
    professional_search = WorkExperienceSearchTool(work_repo=CsvWorkExperienceRepository())
    return ExpertFinderAgent(
        llm=GPTLLM(model=SETTINGS.gpt_model),
        education_search=education_search,
        professional_search=professional_search,
        profile_compare=ProfileComparisonTool(
            education_search=education_search,
            professional_search=professional_search,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Expert Finder POC")
    parser.add_argument(
        "question",
        type=str,
        help="Natural-language query",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="Logging level (e.g., DEBUG, INFO, WARNING)",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)
    agent = build_agent()
    # Re-silence OpenAI/HTTP loggers in case the SDK set DEBUG on import
    silence_third_party_loggers()
    result = agent.run(args.question)

    formatted_results = [{'name': e.name, 'reason': e.reason} for e in result.experts]
    print(json.dumps({"question": args.question, "result": formatted_results}, indent=2))


    # print(json.dumps({"question": args.question, "result": result.model_dump()}, indent=2))

if __name__ == "__main__":
    main()
