"""CLI entrypoint for the Expert Finder POC."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from expert_finder.application.deps import get_agent
from expert_finder.application.deps import get_llm
from expert_finder.config.settings import AgentSettings
from expert_finder.domain.agents.expert_finder import ExpertFinderAgent
from expert_finder.domain.agents.expert_finder import ExpertFinderRunOutput
from expert_finder.config.settings import get_agent_settings
from expert_finder.config.settings import SupportedModel
from expert_finder.entrypoints.cli.presentation import emit_json_compat
from expert_finder.entrypoints.cli.presentation import render_experts_table
from expert_finder.entrypoints.cli.presentation import render_metrics_table
from expert_finder.entrypoints.cli.presentation import render_profiles_table
from expert_finder.entrypoints.cli.samples import run_samples_to_file
from expert_finder.entrypoints.cli.types import OutputFormat
from expert_finder.infrastructure.logging import setup_logging, silence_third_party_loggers
from expert_finder.infrastructure.path import SAMPLE_REQUESTS_JSON, SAMPLE_REQUESTS_RESULTS_JSON

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    help="Find experts for a natural-language query.",
)
console = Console()
CURRENT_DEFAULT_MODEL = get_agent_settings().gpt_model.value


def get_agent_modified(*, model: SupportedModel | None) -> ExpertFinderAgent:
    settings: AgentSettings = get_agent_settings()
    if model is not None:
        settings = settings.model_copy(update={"gpt_model": model})

    llm = get_llm(settings=settings)
    return get_agent(llm=llm)


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
    agent = get_agent_modified(model=model)
    # Re-silence OpenAI/HTTP loggers in case the SDK set DEBUG on import
    silence_third_party_loggers()
    run_output = agent.run_with_metrics(question)

    if output in (OutputFormat.table, OutputFormat.both):
        console.print(render_experts_table(run_output))
        if show_metrics:
            console.print(render_metrics_table(run_output))
        if profiles_limit > 0:
            console.print(render_profiles_table(run_output.profiles[:profiles_limit]))
        if show_context:
            grid = Table.grid(padding=(0, 1))
            grid.add_row(
                "[bold]Query parameters[/bold]",
                json.dumps(run_output.query_parameters, indent=2),
            )
            console.print(grid)

    if output in (OutputFormat.json, OutputFormat.both):
        # Default JSON is kept compatible with the previous CLI output.
        emit_json_compat(run_output, profiles_limit=profiles_limit)


@app.command("answer")
def answer(
    question: Annotated[
        str,
        typer.Argument(
            help="Natural-language query.",
        ),
    ],
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
            help=f"LLM model override (current default: {CURRENT_DEFAULT_MODEL}).",
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
    """Answer a single question using the expert finder agent."""
    _run(
        question,
        model=model,
        log_level=log_level,
        output=output,
        profiles_limit=profiles_limit,
        show_metrics=show_metrics,
        show_context=show_context,
    )


@app.command("batch")
def batch(
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
            help=f"LLM model override (current default: {CURRENT_DEFAULT_MODEL}).",
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
    """Run the sample question batch and save the output JSON."""
    setup_logging(log_level)
    silence_third_party_loggers()
    run_samples_to_file(
        agent=get_agent_modified(model=model),
        input_file=input_file,
        output_file=output_file,
        limit=limit,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
