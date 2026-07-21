import json
import subprocess
from pathlib import Path

import pytest
import tomlkit
import yaml

from cyber_junshi.adapters import install_adapter, render_adapter


def test_all_adapter_previews_launch_the_same_stdio_server(tmp_path: Path) -> None:
    for agent in ("hermes", "openclaw", "codex", "claude-desktop"):
        rendered = render_adapter(agent, home=tmp_path, system_name="Windows")
        assert "uvx" in rendered.preview
        assert "git+https://github.com/AITCX08/cyber-junshi" in rendered.preview
        assert "cyber-junshi" in rendered.preview
        assert "serve" in rendered.preview


def test_preview_never_writes_a_configuration(tmp_path: Path) -> None:
    result = install_adapter("hermes", apply=False, home=tmp_path)

    assert not result.applied
    assert not (tmp_path / ".hermes" / "config.yaml").exists()


def test_hermes_apply_preserves_unrelated_config_and_is_idempotent(tmp_path: Path) -> None:
    target = tmp_path / ".hermes" / "config.yaml"
    target.parent.mkdir(parents=True)
    target.write_text("theme: dark\n", encoding="utf-8")

    first = install_adapter("hermes", apply=True, home=tmp_path)
    second = install_adapter("hermes", apply=True, home=tmp_path)
    parsed = yaml.safe_load(target.read_text(encoding="utf-8"))

    assert first.changed
    assert first.backup_path is not None and first.backup_path.exists()
    assert not second.changed
    assert parsed["theme"] == "dark"
    assert parsed["mcp_servers"]["cyber_junshi"] == {
        "command": "uvx",
        "args": [
            "--from",
            "git+https://github.com/AITCX08/cyber-junshi",
            "cyber-junshi",
            "serve",
        ],
    }


def test_codex_apply_preserves_existing_toml(tmp_path: Path) -> None:
    target = tmp_path / ".codex" / "config.toml"
    target.parent.mkdir(parents=True)
    target.write_text('model = "example-model"\n', encoding="utf-8")

    result = install_adapter("codex", apply=True, home=tmp_path)
    parsed = tomlkit.parse(target.read_text(encoding="utf-8"))

    assert result.changed
    assert parsed["model"] == "example-model"
    assert parsed["mcp_servers"]["cyber_junshi"]["command"] == "uvx"
    assert list(parsed["mcp_servers"]["cyber_junshi"]["args"]) == [
        "--from",
        "git+https://github.com/AITCX08/cyber-junshi",
        "cyber-junshi",
        "serve",
    ]


def test_claude_apply_preserves_existing_json(tmp_path: Path) -> None:
    target = tmp_path / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"appearance": "dark"}), encoding="utf-8")

    result = install_adapter(
        "claude-desktop", apply=True, home=tmp_path, system_name="Windows"
    )
    parsed = json.loads(target.read_text(encoding="utf-8"))

    assert result.changed
    assert parsed["appearance"] == "dark"
    assert parsed["mcpServers"]["cyber-junshi"]["args"] == [
        "--from",
        "git+https://github.com/AITCX08/cyber-junshi",
        "cyber-junshi",
        "serve",
    ]


def test_malformed_configuration_is_never_replaced(tmp_path: Path) -> None:
    target = tmp_path / ".hermes" / "config.yaml"
    target.parent.mkdir(parents=True)
    original = "mcp_servers: [unterminated"
    target.write_text(original, encoding="utf-8")

    with pytest.raises(ValueError, match="parse"):
        install_adapter("hermes", apply=True, home=tmp_path)

    assert target.read_text(encoding="utf-8") == original


def test_openclaw_apply_executes_argument_list_without_shell(tmp_path: Path) -> None:
    calls: list[tuple[tuple[str, ...], bool, bool]] = []

    def runner(command, *, check, shell):
        calls.append((tuple(command), check, shell))
        return subprocess.CompletedProcess(command, 0)

    result = install_adapter("openclaw", apply=True, home=tmp_path, runner=runner)

    assert result.changed
    assert calls == [
        (
            (
                "openclaw",
                "mcp",
                "add",
                "cyber-junshi",
                "--command",
                "uvx",
                "--arg",
                "--from",
                "--arg",
                "git+https://github.com/AITCX08/cyber-junshi",
                "--arg",
                "cyber-junshi",
                "--arg",
                "serve",
            ),
            True,
            False,
        )
    ]


def test_unknown_agent_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="supported"):
        render_adapter("unknown", home=tmp_path)
