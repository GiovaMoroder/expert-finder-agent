import json
import time

from expert_finder.expert_finder.agent.expert_finder import ExpertFinderAgent
from expert_finder.expert_finder.config import SETTINGS
from expert_finder.expert_finder.llm.adapters.gpt import GPTLLM
from expert_finder.expert_finder.path import SAMPLE_REQUESTS_JSON, SAMPLE_REQUESTS_RESULTS_JSON
from expert_finder.expert_finder.tools.education_search import EducationSearchTool
from expert_finder.expert_finder.tools.work_experience_search import WorkExperienceSearchTool
from expert_finder.expert_finder.tools.profile_compare import ProfileComparisonTool


def main() -> None:
    questions = json.loads(SAMPLE_REQUESTS_JSON.read_text(encoding="utf-8"))

    education_search = EducationSearchTool()
    professional_search = WorkExperienceSearchTool()
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
        result, metrics = agent.run_with_metrics(question)
        elapsed = time.perf_counter() - start_time
        results.append(
            {
                "id": item.get("id"),
                "question": question,
                "result": result.model_dump(),
                "candidate_metrics": metrics,
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
