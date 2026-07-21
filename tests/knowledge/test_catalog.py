from pathlib import Path

import yaml

from cyber_junshi.knowledge.catalog import validate_catalog

ROOT = Path(__file__).resolve().parents[2]


def _write_catalog(root: Path, item_overrides: dict[str, object] | None = None) -> None:
    (root / "knowledge" / "core").mkdir(parents=True)
    (root / "knowledge" / "core" / "card.md").write_text("# Independent card\n", "utf-8")
    source = {
        "id": "project-source",
        "title": "Project source",
        "publisher": "Project",
        "url": "project://README.md",
        "source_type": "project_original",
        "use_mode": "apache_2_original",
        "commercial_allowed": True,
        "verified_at": "2026-07-22",
    }
    item: dict[str, object] = {
        "id": "core-card",
        "path": "knowledge/core/card.md",
        "topic": "test",
        "evidence_level": "E0",
        "source_ids": ["project-source"],
        "source_type": "project_original",
        "commercial_allowed": True,
        "creation_mode": "project_original",
        "reviewed_at": "2026-07-22",
    }
    item.update(item_overrides or {})
    (root / "knowledge" / "sources.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "sources": [source]}, sort_keys=False),
        "utf-8",
    )
    (root / "knowledge" / "catalog.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "items": [item]}, sort_keys=False),
        "utf-8",
    )


def test_checked_in_catalog_contains_34_independent_items() -> None:
    report = validate_catalog(ROOT)

    assert report.item_count == 34
    assert report.errors == ()


def test_valid_catalog_passes(tmp_path: Path) -> None:
    _write_catalog(tmp_path)

    report = validate_catalog(tmp_path)

    assert report.item_count == 1
    assert report.errors == ()


def test_missing_required_field_is_reported(tmp_path: Path) -> None:
    _write_catalog(tmp_path, {"reviewed_at": None})

    report = validate_catalog(tmp_path)

    assert any("reviewed_at" in error for error in report.errors)


def test_unknown_source_is_reported(tmp_path: Path) -> None:
    _write_catalog(tmp_path, {"source_ids": ["unknown-source"]})

    report = validate_catalog(tmp_path)

    assert any("unknown-source" in error for error in report.errors)


def test_missing_document_is_reported(tmp_path: Path) -> None:
    _write_catalog(tmp_path, {"path": "knowledge/core/missing.md"})

    report = validate_catalog(tmp_path)

    assert any("missing.md" in error for error in report.errors)


def test_path_cannot_escape_repository(tmp_path: Path) -> None:
    _write_catalog(tmp_path, {"path": "../outside.md"})

    report = validate_catalog(tmp_path)

    assert any("outside repository" in error for error in report.errors)


def test_upstream_paraphrase_mode_is_rejected(tmp_path: Path) -> None:
    _write_catalog(tmp_path, {"creation_mode": "upstream_paraphrase"})

    report = validate_catalog(tmp_path)

    assert any("creation_mode" in error for error in report.errors)


def test_discovery_repository_cannot_be_a_content_source(tmp_path: Path) -> None:
    _write_catalog(tmp_path)
    sources_path = tmp_path / "knowledge" / "sources.yaml"
    payload = yaml.safe_load(sources_path.read_text("utf-8"))
    payload["sources"][0]["url"] = "https://github.com/powerycy/goutoujunshi"
    sources_path.write_text(yaml.safe_dump(payload, sort_keys=False), "utf-8")

    report = validate_catalog(tmp_path)

    assert any("discovery-only" in error for error in report.errors)
