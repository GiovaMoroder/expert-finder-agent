import json
import time

from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.tools.education_search import EducationSearchTool
from expert_finder.domain.tools.profile_compare import ProfileComparisonTool
from expert_finder.domain.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.infrastructure.config import SETTINGS
from expert_finder.infrastructure.llm.adapters.gpt import GPTLLM
from expert_finder.infrastructure.path import SAMPLE_REQUESTS_JSON, SAMPLE_REQUESTS_RESULTS_JSON
from expert_finder.infrastructure.persistence.csv.education_repo import CsvEducationRepository
from expert_finder.infrastructure.persistence.csv.work_experience_repo import CsvWorkExperienceRepository


def main() -> None:
    questions = json.loads(SAMPLE_REQUESTS_JSON.read_text(encoding="utf-8"))

    education_search = EducationSearchTool(education_repo=CsvEducationRepository())
    professional_search = WorkExperienceSearchTool(work_repo=CsvWorkExperienceRepository())
    agent = ExpertFinderAgent(
        llm=GPTLLM(model=SETTINGS.gpt_model),
        education_search=education_search,
        professional_search=professional_search,
        profile_compare=ProfileComparisonTool(
            education_search=education_search,
            professional_search=professional_search,
        ),
    )

    results = []
    for i, item in enumerate(questions):
        question = item.get("text", "")
        start_time = time.perf_counter()
        result, metrics, query_parameters, profiles = agent.run_with_metrics(question)
        elapsed = time.perf_counter() - start_time
        results.append(
            {
                "id": item.get("id"),
                "question": question,
                "result": result.model_dump(),
                "candidate_metrics": metrics,
                "profiles": profiles,
                "query_parameters": query_parameters,
                "elapsed_seconds": round(elapsed, 3),
            }
        )
        print(f"Processed question {i + 1}/{len(questions)} in {elapsed:.2f}s")

    SAMPLE_REQUESTS_RESULTS_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {SAMPLE_REQUESTS_RESULTS_JSON} with {len(results)} results")


if __name__ == "__main__":
    main()
