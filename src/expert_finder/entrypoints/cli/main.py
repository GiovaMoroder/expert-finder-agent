"""CLI entrypoint for the Expert Finder POC."""

from __future__ import annotations

import json
import time
from enum import Enum
from pathlib import Path
from collections.abc import Callable
from typing import Annotated
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from expert_finder.application.deps import build_agent
from expert_finder.config.settings import AgentSettings
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.agents.expert_finder import ExpertFinderRunOutput
from expert_finder.config.settings import get_agent_settings
from expert_finder.config.settings import SupportedModel
from expert_finder.infrastructure.logging import setup_logging, silence_third_party_loggers
from expert_finder.infrastructure.path import SAMPLE_REQUESTS_JSON, SAMPLE_REQUESTS_RESULTS_JSON

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    help="Find experts for a natural-language query.",
)
console = Console()


class OutputFormat(str, Enum):
    json = "json"
    table = "table"
    both = "both"


def _render_experts_table(run_output: ExpertFinderRunOutput) -> Table:
    table = Table(title="Recommended experts")
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Reason", style="white")
    for idx, expert in enumerate(run_output.result.experts, start=1):
        table.add_row(str(idx), expert.name, expert.reason)
    return table


def _render_metrics_table(run_output: ExpertFinderRunOutput) -> Table:
    table = Table(title="Run metrics")
    table.add_column("Metric", style="magenta", no_wrap=True)
    table.add_column("Value", justify="right")
    for k, v in run_output.metrics.items():
        table.add_row(k, str(v))
    return table


def _render_profiles_table(profiles: list[dict[str, Any]]) -> Table:
    table = Table(title="Top candidate profiles")
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Current title", style="white")
    table.add_column("Institution records", justify="right")
    for idx, profile in enumerate(profiles, start=1):
        table.add_row(
            str(idx),
            str(profile.get("name", "")),
            str(profile.get("current_title", "") or ""),
            str(len(profile.get("institution_records") or [])),
        )
    return table


def _emit_json_compat(run_output: ExpertFinderRunOutput, *, profiles_limit: int) -> None:
    """Keep backwards-compatible JSON output shape (two JSON blobs)."""
    top_profiles = run_output.profiles[:profiles_limit]
    formatted_experts = [{"name": e.name, "reason": e.reason} for e in run_output.result.experts]
    typer.echo(json.dumps({"top_10_profiles": top_profiles}, indent=2))
    typer.echo(json.dumps(formatted_experts, indent=2))


def _cli_settings_provider(*, model: SupportedModel | None) -> Callable[[], AgentSettings]:
    base_settings = get_agent_settings()
    overrides: dict[str, object] = {}
    if model is not None:
        overrides["gpt_model"] = model

    if not overrides:
        return get_agent_settings

    def provider() -> AgentSettings:
        return base_settings.model_copy(update=overrides)

    return provider


def _run(
    question: str,
    *,
    model: SupportedModel | None,
    log_level: str,
    output: OutputFormat,
    profiles_limit: int,
    show_metrics: bool,
    show_context: bool,
) -> None:
    setup_logging(log_level)
    agent = build_agent(settings_provider=_cli_settings_provider(model=model))
    # Re-silence OpenAI/HTTP loggers in case the SDK set DEBUG on import
    silence_third_party_loggers()
    run_output = agent.run_with_metrics(question)

    if output in (OutputFormat.table, OutputFormat.both):
        console.print(_render_experts_table(run_output))
        if show_metrics:
            console.print(_render_metrics_table(run_output))
        if profiles_limit > 0:
            console.print(_render_profiles_table(run_output.profiles[:profiles_limit]))
        if show_context:
            grid = Table.grid(padding=(0, 1))
            grid.add_row(
                "[bold]Query parameters[/bold]",
                json.dumps(run_output.query_parameters, indent=2),
            )
            console.print(grid)

    if output in (OutputFormat.json, OutputFormat.both):
        # Default JSON is kept compatible with the previous CLI output.
        _emit_json_compat(run_output, profiles_limit=profiles_limit)


@app.callback(invoke_without_command=True)
def cli(
    question: Annotated[
        str | None,
        typer.Argument(
            help="Natural-language query.",
        ),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            envvar="LOG_LEVEL",
            help="Logging level (e.g., DEBUG, INFO, WARNING).",
            show_default=True,
        ),
    ] = "INFO",
    model: Annotated[
        SupportedModel | None,
        typer.Option(
            "--model",
            envvar="LLM_MODEL",
            help="LLM model name.",
            show_default=False,
        ),
    ] = None,
    output: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            help="Output format.",
            show_default=True,
            case_sensitive=False,
        ),
    ] = OutputFormat.table,
    profiles_limit: Annotated[
        int,
        typer.Option(
            "--profiles-limit",
            min=0,
            help="Max candidate profiles to display (0 to hide).",
            show_default=True,
        ),
    ] = 10,
    show_metrics: Annotated[
        bool,
        typer.Option(
            "--metrics/--no-metrics",
            help="Show run metrics (table output only).",
            show_default=True,
        ),
    ] = False,
    show_context: Annotated[
        bool,
        typer.Option(
            "--context/--no-context",
            help="Show extracted query parameters (table output only).",
            show_default=True,
        ),
    ] = False,
) -> None:
    """Entry point.

    Supports:
    - `expert-finder "your question"`
    """
    if question is None:
        # With no args, Typer will show help (no_args_is_help=True).
        return
    _run(
        question,
        model=model,
        log_level=log_level,
        output=output,
        profiles_limit=profiles_limit,
        show_metrics=show_metrics,
        show_context=show_context,
    )


@app.command("run-samples")
def run_samples(
    input_file: Annotated[
        Path,
        typer.Option(
            "--input-file",
            help="JSON file with sample questions.",
            show_default=True,
        ),
    ] = SAMPLE_REQUESTS_JSON,
    output_file: Annotated[
        Path,
        typer.Option(
            "--output-file",
            help="Where to write run results JSON.",
            show_default=True,
        ),
    ] = SAMPLE_REQUESTS_RESULTS_JSON,
    model: Annotated[
        SupportedModel | None,
        typer.Option(
            "--model",
            envvar="LLM_MODEL",
            help="LLM model override.",
            show_default=False,
        ),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            envvar="LOG_LEVEL",
            help="Logging level (e.g., DEBUG, INFO, WARNING).",
            show_default=True,
        ),
    ] = "INFO",
    limit: Annotated[
        int | None,
        typer.Option(
            "--limit",
            min=1,
            help="Run only the first N sample questions.",
            show_default=False,
        ),
    ] = None,
) -> None:
    setup_logging(log_level)
    agent = build_agent(settings_provider=_cli_settings_provider(model=model))
    silence_third_party_loggers()

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
