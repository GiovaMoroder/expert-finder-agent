"""Presentation helpers for CLI output."""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.table import Table

from expert_finder.domain.agents.expert_finder import ExpertFinderRunOutput


def render_experts_table(run_output: ExpertFinderRunOutput) -> Table:
    table = Table(title="Recommended experts")
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Reason", style="white")
    for idx, expert in enumerate(run_output.result.experts, start=1):
        table.add_row(str(idx), expert.name, expert.reason)
    return table


def render_metrics_table(run_output: ExpertFinderRunOutput) -> Table:
    table = Table(title="Run metrics")
    table.add_column("Metric", style="magenta", no_wrap=True)
    table.add_column("Value", justify="right")
    for k, v in run_output.metrics.items():
        table.add_row(k, str(v))
    return table


def render_profiles_table(profiles: list[dict[str, Any]]) -> Table:
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


def emit_json_compat(run_output: ExpertFinderRunOutput, *, profiles_limit: int) -> None:
    """Keep backwards-compatible JSON output shape (two JSON blobs)."""
    top_profiles = run_output.profiles[:profiles_limit]
    formatted_experts = [{"name": e.name, "reason": e.reason} for e in run_output.result.experts]
    typer.echo(json.dumps({"top_10_profiles": top_profiles}, indent=2))
    typer.echo(json.dumps(formatted_experts, indent=2))
