"""FastMCP stdio server exposing the public Cyber Junshi tool surface."""

import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from cyber_junshi.core.decision import (
    compare_options as compare_option_values,
)
from cyber_junshi.core.decision import (
    create_action_plan as build_action_plan,
)
from cyber_junshi.core.decision import (
    structure_case as build_fact_layers,
)
from cyber_junshi.core.models import OptionInput
from cyber_junshi.core.safety import assess_safety as assess_safety_text
from cyber_junshi.storage.sqlite import DecisionStore

_INSTRUCTIONS = (
    "Run assess_safety first whenever immediate harm, coercion, stalking, or threats may be "
    "present. Keep facts, inferences, and unknowns separate. Compare explicit costs before "
    "choosing an action, and create stop conditions before acting. Persist an outcome only "
    "when the user explicitly asks to record it."
)


def default_database_path() -> Path:
    """Resolve the local database path without creating it."""

    configured = os.environ.get("CYBER_JUNSHI_DB")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".cyber-junshi" / "cyber-junshi.db"


def _plan_dict(plan: Any) -> dict[str, object]:
    data = asdict(plan)
    return {
        "action": data["action"],
        "observation_hours": data["observation_hours"],
        "success_signals": list(data["success_signals"]),
        "downgrade_signals": list(data["downgrade_signals"]),
        "stop_signals": list(data["stop_signals"]),
    }


def create_server(database_path: Path | None = None) -> FastMCP:
    """Create an isolated MCP server backed by one explicit local database."""

    store = DecisionStore(database_path or default_database_path())
    server = FastMCP("Cyber Junshi", instructions=_INSTRUCTIONS)

    @server.tool()
    def assess_safety(text: str) -> dict[str, object]:
        """Read-only: screen text for normal, elevated, or emergency routing."""

        assessment = assess_safety_text(text)
        return {
            "level": assessment.level.value,
            "reasons": list(assessment.reasons),
            "next_steps": list(assessment.next_steps),
        }

    @server.tool()
    def structure_case(
        facts: list[str],
        inferences: list[str],
        unknowns: list[str],
    ) -> dict[str, object]:
        """Read-only: separate observations, interpretations, and missing information."""

        layers = build_fact_layers(facts, inferences, unknowns)
        return {
            "facts": list(layers.facts),
            "inferences": list(layers.inferences),
            "unknowns": list(layers.unknowns),
        }

    @server.tool()
    def compare_options(options: list[dict[str, Any]]) -> dict[str, object]:
        """Read-only: rank two or more explicit options with transparent 0..10 metrics."""

        try:
            option_values = [OptionInput(**option) for option in options]
        except TypeError as exc:
            raise ValueError(f"invalid option fields: {exc}") from exc
        ranked = compare_option_values(option_values)
        return {"options": [asdict(option) for option in ranked]}

    @server.tool()
    def create_action_plan(
        action: str,
        observation_hours: int,
        success_signals: list[str],
        downgrade_signals: list[str],
        stop_signals: list[str],
    ) -> dict[str, object]:
        """Read-only: define one bounded action and its downgrade and stop conditions."""

        plan = build_action_plan(
            action,
            observation_hours,
            success_signals,
            downgrade_signals,
            stop_signals,
        )
        return _plan_dict(plan)

    @server.tool()
    def record_outcome(
        case_id: str,
        action: str,
        observation_hours: int,
        success_signals: list[str],
        downgrade_signals: list[str],
        stop_signals: list[str],
        observed_signals: list[str],
        note: str = "",
    ) -> dict[str, object]:
        """Local write: explicitly save one synthetic or user-approved decision outcome."""

        plan = build_action_plan(
            action,
            observation_hours,
            success_signals,
            downgrade_signals,
            stop_signals,
        )
        record_id = store.record_outcome(case_id, plan, observed_signals, note)
        return {"record_id": record_id, "database": str(store.path)}

    @server.tool()
    def review_decision(record_id: str) -> dict[str, object]:
        """Read-only: review one outcome already stored in the local database."""

        return store.review_decision(record_id)

    return server


def run_server() -> None:
    """Run the MCP server over stdio."""

    create_server().run(transport="stdio")


if __name__ == "__main__":
    run_server()
