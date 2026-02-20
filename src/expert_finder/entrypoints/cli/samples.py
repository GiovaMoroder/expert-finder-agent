"""Sample-run processing helpers for CLI commands."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import typer

from expert_finder.domain.agents.expert_finder import ExpertFinderAgent


def run_samples_to_file(
    *,
    agent: ExpertFinderAgent,
    input_file: Path,
    output_file: Path,
    limit: int | None,
) -> None:
    payload = json.loads(input_file.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise typer.BadParameter("Sample input must be a JSON array.", param_hint="--input-file")
    questions: list[dict[str, Any]] = payload
    if limit is not None:
        questions = questions[:limit]

    results: list[dict[str, Any]] = []
    total = len(questions)
    for idx, item in enumerate(questions, start=1):
        question = str(item.get("text", ""))
        start_time = time.perf_counter()
        run_output = agent.run_with_metrics(question)
        elapsed = time.perf_counter() - start_time

        results.append(
            {
                "id": item.get("id"),
                "question": question,
                "result": run_output.result.model_dump(mode="json"),
                "candidate_metrics": run_output.metrics,
                "profiles": run_output.profiles,
                "query_parameters": run_output.query_parameters,
                "elapsed_seconds": round(elapsed, 3),
            }
        )
        typer.echo(f"Processed question {idx}/{total} in {elapsed:.2f}s")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    typer.echo(f"Wrote {output_file} with {len(results)} results")
