"""Safe configuration plans for supported personal Agent ecosystems."""

import json
import os
import platform
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import tomlkit
import yaml

_SUPPORTED_AGENTS = ("hermes", "openclaw", "codex", "claude-desktop")
_STDIO_COMMAND = "uvx"
_SOURCE_URL = "git+https://github.com/AITCX08/cyber-junshi"
_STDIO_ARGS = ["--from", _SOURCE_URL, "cyber-junshi", "serve"]
_OPENCLAW_COMMAND = (
    "openclaw",
    "mcp",
    "add",
    "cyber-junshi",
    "--command",
    "uvx",
    "--arg",
    "--from",
    "--arg",
    _SOURCE_URL,
    "--arg",
    "cyber-junshi",
    "--arg",
    "serve",
)


@dataclass(frozen=True)
class AdapterPlan:
    """A side-effect-free preview of one client integration."""

    agent: str
    target_path: Path | None
    preview: str
    command: tuple[str, ...] | None = None


@dataclass(frozen=True)
class AdapterResult:
    """Result of previewing or applying an adapter plan."""

    agent: str
    applied: bool
    changed: bool
    target_path: Path | None
    backup_path: Path | None
    preview: str


def _normalized_agent(agent: str) -> str:
    normalized = agent.strip().casefold() if isinstance(agent, str) else ""
    if normalized not in _SUPPORTED_AGENTS:
        supported = ", ".join(_SUPPORTED_AGENTS)
        raise ValueError(f"agent must be one of the supported values: {supported}")
    return normalized


def _home_path(home: Path | None) -> Path:
    return (home or Path.home()).expanduser().resolve()


def _claude_path(home: Path, system_name: str) -> Path:
    if system_name.casefold() == "windows":
        return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    if system_name.casefold() == "darwin":
        return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    return home / ".config" / "Claude" / "claude_desktop_config.json"


def render_adapter(
    agent: str,
    *,
    home: Path | None = None,
    system_name: str | None = None,
) -> AdapterPlan:
    """Render a client integration without reading or writing its configuration."""

    normalized = _normalized_agent(agent)
    resolved_home = _home_path(home)
    if normalized == "hermes":
        preview = yaml.safe_dump(
            {
                "mcp_servers": {
                    "cyber_junshi": {"command": _STDIO_COMMAND, "args": _STDIO_ARGS}
                }
            },
            allow_unicode=True,
            sort_keys=False,
        )
        return AdapterPlan(normalized, resolved_home / ".hermes" / "config.yaml", preview)
    if normalized == "openclaw":
        return AdapterPlan(normalized, None, " ".join(_OPENCLAW_COMMAND), _OPENCLAW_COMMAND)
    if normalized == "codex":
        preview = (
            "[mcp_servers.cyber_junshi]\n"
            f'command = "{_STDIO_COMMAND}"\n'
            f'args = ["--from", "{_SOURCE_URL}", "cyber-junshi", "serve"]\n'
        )
        return AdapterPlan(normalized, resolved_home / ".codex" / "config.toml", preview)

    target = _claude_path(resolved_home, system_name or platform.system())
    preview = json.dumps(
        {
            "mcpServers": {
                "cyber-junshi": {"command": _STDIO_COMMAND, "args": _STDIO_ARGS}
            }
        },
        ensure_ascii=False,
        indent=2,
    )
    return AdapterPlan(normalized, target, preview)


def _merge_hermes(existing: str) -> str:
    try:
        document = yaml.safe_load(existing) if existing.strip() else {}
    except yaml.YAMLError as exc:
        raise ValueError("could not parse existing Hermes YAML configuration") from exc
    if not isinstance(document, dict):
        raise ValueError("could not parse existing Hermes configuration as a mapping")
    servers = document.setdefault("mcp_servers", {})
    if not isinstance(servers, dict):
        raise ValueError("could not parse Hermes mcp_servers as a mapping")
    servers["cyber_junshi"] = {"command": _STDIO_COMMAND, "args": _STDIO_ARGS}
    return yaml.safe_dump(document, allow_unicode=True, sort_keys=False)


def _merge_codex(existing: str) -> str:
    try:
        document = tomlkit.parse(existing)
    except Exception as exc:
        raise ValueError("could not parse existing Codex TOML configuration") from exc
    servers = document.get("mcp_servers")
    if servers is None:
        servers = tomlkit.table()
        document["mcp_servers"] = servers
    if not hasattr(servers, "__setitem__"):
        raise ValueError("could not parse Codex mcp_servers as a table")
    entry = tomlkit.table()
    entry.add("command", _STDIO_COMMAND)
    entry.add("args", _STDIO_ARGS)
    servers["cyber_junshi"] = entry
    return tomlkit.dumps(document)


def _merge_claude(existing: str) -> str:
    try:
        document = json.loads(existing) if existing.strip() else {}
    except json.JSONDecodeError as exc:
        raise ValueError("could not parse existing Claude Desktop JSON configuration") from exc
    if not isinstance(document, dict):
        raise ValueError("could not parse existing Claude Desktop configuration as an object")
    servers = document.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError("could not parse Claude Desktop mcpServers as an object")
    servers["cyber-junshi"] = {"command": _STDIO_COMMAND, "args": _STDIO_ARGS}
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def _write_atomically_with_backup(target: Path, content: str) -> tuple[bool, Path | None]:
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    if existing == content:
        return False, None

    target.parent.mkdir(parents=True, exist_ok=True)
    backup_path: Path | None = None
    if target.exists():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_path = target.with_name(f"{target.name}.bak-{timestamp}")
        shutil.copy2(target, backup_path)

    temporary_path = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    try:
        temporary_path.write_text(content, encoding="utf-8")
        os.replace(temporary_path, target)
    finally:
        temporary_path.unlink(missing_ok=True)
    return True, backup_path


def install_adapter(
    agent: str,
    *,
    apply: bool = False,
    home: Path | None = None,
    system_name: str | None = None,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> AdapterResult:
    """Preview or explicitly apply one safe, scoped client integration."""

    plan = render_adapter(agent, home=home, system_name=system_name)
    if not apply:
        return AdapterResult(plan.agent, False, False, plan.target_path, None, plan.preview)

    if plan.command is not None:
        runner(plan.command, check=True, shell=False)
        return AdapterResult(plan.agent, True, True, None, None, plan.preview)

    if plan.target_path is None:
        raise RuntimeError("file adapter did not provide a target path")
    existing = (
        plan.target_path.read_text(encoding="utf-8") if plan.target_path.exists() else ""
    )
    if plan.agent == "hermes":
        merged = _merge_hermes(existing)
    elif plan.agent == "codex":
        merged = _merge_codex(existing)
    else:
        merged = _merge_claude(existing)
    changed, backup_path = _write_atomically_with_backup(plan.target_path, merged)
    return AdapterResult(
        plan.agent,
        True,
        changed,
        plan.target_path,
        backup_path,
        plan.preview,
    )
