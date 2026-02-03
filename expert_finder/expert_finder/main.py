"""CLI entrypoint for the Expert Finder POC."""

from __future__ import annotations

import argparse
import json
import os

from expert_finder.expert_finder.agent.expert_finder import ExpertFinderAgent
from expert_finder.expert_finder.config import SETTINGS
from expert_finder.expert_finder.llm.gpt import GPTLLM
from expert_finder.expert_finder.llm.stub import DeterministicStubLLM
from expert_finder.expert_finder.logging import setup_logging
from expert_finder.expert_finder.tools.education_search import EducationSearchTool
from expert_finder.expert_finder.tools.institution_search import ProfessionalSearchTool
from expert_finder.expert_finder.tools.profile_compare import ProfileComparisonTool


def build_agent() -> ExpertFinderAgent:
    education_search = EducationSearchTool()
    professional_search = ProfessionalSearchTool()
    return ExpertFinderAgent(
        llm=GPTLLM(model=SETTINGS.gpt_model),
        education_search=education_search,
        professional_search=professional_search,
        profile_compare=ProfileComparisonTool(
            education_search=education_search,
            professional_search=professional_search,
        ),
    )


DEFAULT_QUESTIONS = [
    # "Qualcuno ha frequentato Standord nel dipartimento di CS?",
    # "Who has experience in NLP at Meta?",
    # "Qualcuno ha studiato a Stanford?",
    "Qualcuno ha esperienza di NLP a Meta?"
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Expert Finder POC")
    parser.add_argument(
        "questions",
        nargs="*",
        type=str,
        help="Natural-language query (optional; uses examples if omitted)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="Logging level (e.g., DEBUG, INFO, WARNING)",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)
    # setup_logging('DEBUG')

    questions = args.questions or DEFAULT_QUESTIONS

    agent = build_agent()
    for question in questions:
        result = agent.run(question)
        print(json.dumps({"question": question, "result": result.model_dump()}, indent=2))


if __name__ == "__main__":
    # TODO: This is where a FastAPI app would invoke the agent in production.
    # TODO: This is where a Slack bot handler would invoke the agent in production.
    main()
