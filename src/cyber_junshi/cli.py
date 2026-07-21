"""Command-line interface for local Cyber Junshi usage."""

import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

import typer

from cyber_junshi.adapters import install_adapter
from cyber_junshi.core.decision import compare_options, structure_case
from cyber_junshi.core.models import OptionInput
from cyber_junshi.core.safety import assess_safety
from cyber_junshi.knowledge.catalog import validate_catalog
from cyber_junshi.mcp.server import create_server, run_server

app = typer.Typer(
    name="cyber-junshi",
    help="Local-first decision support for personal Agents.",
    no_args_is_help=True,
)


@app.command()
def serve() -> None:
    """Run the MCP server over stdio."""

    run_server()


@app.command()
def install(
    agent: Annotated[str, typer.Argument(help="Hermes, OpenClaw, Codex, or Claude Desktop")],
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Write the scoped config or run the official client CLI."),
    ] = False,
    home: Annotated[
        Path | None,
        typer.Option("--home", help="Override HOME for isolated setup or testing."),
    ] = None,
) -> None:
    """Preview an Agent integration; write only with --apply."""

    try:
        result = install_adapter(agent, apply=apply, home=home)
    except (OSError, ValueError) as exc:
        typer.echo(f"Install failed: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    if not apply:
        typer.echo("Preview only (no files changed):")
        typer.echo(result.preview)
        typer.echo("Run the same command with --apply to install.")
        return
    if result.changed:
        typer.echo(f"Applied {result.agent} integration.")
    else:
        typer.echo(f"Already configured: {result.agent}.")
    if result.target_path:
        typer.echo(f"Target: {result.target_path}")
    if result.backup_path:
        typer.echo(f"Backup: {result.backup_path}")


@app.command()
def doctor(
    home: Annotated[
        Path | None,
        typer.Option("--home", help="Reserved for isolated diagnostics."),
    ] = None,
) -> None:
    """Check Python, local SQLite creation, and MCP tool discovery."""

    del home
    report: dict[str, object] = {
        "python": "healthy" if sys.version_info >= (3, 10) else "unsupported",
        "storage": "unhealthy",
        "mcp": "unhealthy",
    }
    try:
        with TemporaryDirectory(prefix="cyber-junshi-doctor-") as directory:
            database_path = Path(directory) / "doctor.db"
            server = create_server(database_path)
            tools = asyncio.run(server.list_tools())
            report["storage"] = "healthy" if database_path.is_file() else "unhealthy"
            report["mcp"] = "healthy" if len(tools) == 11 else "unhealthy"
            report["tool_count"] = len(tools)
    except Exception as exc:
        report["error"] = type(exc).__name__
    typer.echo(json.dumps(report, ensure_ascii=False))
    if any(report[key] != "healthy" for key in ("python", "storage", "mcp")):
        raise typer.Exit(code=1)


@app.command()
def audit_knowledge(
    root: Annotated[
        Path | None,
        typer.Option("--root", help="Repository root containing knowledge/catalog.yaml."),
    ] = None,
) -> None:
    """Validate knowledge provenance, source links, and checked-in document paths."""

    report = validate_catalog(root or Path.cwd())
    typer.echo(
        json.dumps(
            {"item_count": report.item_count, "errors": list(report.errors)},
            ensure_ascii=False,
        )
    )
    if report.errors:
        raise typer.Exit(code=1)


@app.command()
def demo() -> None:
    """Print one fictional decision cycle without writing user data."""

    safety = assess_safety("我们下周再约时间聊")
    layers = structure_case(
        ["对方取消了一次见面"],
        ["对方可能在回避"],
        ["取消的具体原因"],
    )
    options = compare_options(
        [
            OptionInput("连续追问", 8, 8, 2, 8, 2),
            OptionInput("澄清一次并观察", 6, 2, 9, 3, 8),
        ]
    )
    payload = {
        "synthetic": True,
        "safety": {
            "level": safety.level.value,
            "reasons": list(safety.reasons),
            "next_steps": list(safety.next_steps),
        },
        "case": {
            "facts": list(layers.facts),
            "inferences": list(layers.inferences),
            "unknowns": list(layers.unknowns),
        },
        "options": [asdict(option) for option in options],
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
