import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_release_files_exist() -> None:
    required = {
        "README.md",
        "README.zh-CN.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "Dockerfile",
        "docker-compose.yml",
        ".github/workflows/ci.yml",
        "examples/synthetic_case.json",
    }

    missing = sorted(path for path in required if not (ROOT / path).is_file())

    assert missing == []


def test_readmes_document_safe_install_and_all_clients() -> None:
    for readme_name in ("README.md", "README.zh-CN.md"):
        content = (ROOT / readme_name).read_text(encoding="utf-8")
        assert "uvx cyber-junshi serve" in content
        assert "--apply" in content
        for agent in ("hermes", "openclaw", "codex", "claude-desktop"):
            assert f"cyber-junshi install {agent}" in content


def test_example_is_explicitly_synthetic_and_contains_no_raw_chat() -> None:
    example = json.loads((ROOT / "examples" / "synthetic_case.json").read_text("utf-8"))

    assert example["synthetic"] is True
    assert example["case_id"].startswith("synthetic-")
    assert "raw_chat" not in example
    assert set(example["case"]) == {"facts", "inferences", "unknowns"}


def test_each_adapter_has_a_scoped_guide() -> None:
    for agent in ("hermes", "openclaw", "codex", "claude-desktop"):
        guide = (ROOT / "adapters" / agent / "README.md").read_text(encoding="utf-8")
        assert f"cyber-junshi install {agent}" in guide
        assert "--apply" in guide
