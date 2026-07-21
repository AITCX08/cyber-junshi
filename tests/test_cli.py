import json
from pathlib import Path

from typer.testing import CliRunner

from cyber_junshi.cli import app

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]


def test_install_previews_by_default_without_writing(tmp_path: Path) -> None:
    result = runner.invoke(app, ["install", "hermes", "--home", str(tmp_path)])

    assert result.exit_code == 0
    assert "Preview only" in result.stdout
    assert not (tmp_path / ".hermes" / "config.yaml").exists()


def test_install_applies_only_with_explicit_flag(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["install", "hermes", "--home", str(tmp_path), "--apply"]
    )

    assert result.exit_code == 0
    assert "Applied" in result.stdout
    assert (tmp_path / ".hermes" / "config.yaml").exists()


def test_doctor_reports_local_components_healthy(tmp_path: Path) -> None:
    result = runner.invoke(app, ["doctor", "--home", str(tmp_path)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["python"] == "healthy"
    assert payload["storage"] == "healthy"
    assert payload["mcp"] == "healthy"
    assert payload["tool_count"] == 11


def test_audit_knowledge_reports_checked_in_catalog() -> None:
    result = runner.invoke(app, ["audit-knowledge", "--root", str(ROOT)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload == {"item_count": 34, "errors": []}


def test_audit_knowledge_fails_for_missing_manifests(tmp_path: Path) -> None:
    result = runner.invoke(app, ["audit-knowledge", "--root", str(tmp_path)])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["item_count"] == 0
    assert payload["errors"]


def test_demo_is_synthetic_and_structured() -> None:
    result = runner.invoke(app, ["demo"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["synthetic"] is True
    assert payload["safety"]["level"] == "normal"
    assert len(payload["options"]) == 2
