"""Validate the public knowledge pack and its provenance declarations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_ITEM_FIELDS = {
    "id",
    "path",
    "topic",
    "evidence_level",
    "source_ids",
    "source_type",
    "commercial_allowed",
    "creation_mode",
    "reviewed_at",
}
_SOURCE_FIELDS = {
    "id",
    "title",
    "publisher",
    "url",
    "source_type",
    "use_mode",
    "commercial_allowed",
    "verified_at",
}
_EVIDENCE_LEVELS = {"E0", "E1", "E2", "E3"}
_CREATION_MODES = {
    "project_original",
    "primary_source_rewrite",
    "official_source_rewrite",
}
_DISCOVERY_ONLY_MARKER = "goutoujunshi"


@dataclass(frozen=True)
class CatalogReport:
    """One deterministic knowledge catalog audit result."""

    item_count: int
    errors: tuple[str, ...]


def _load_mapping(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing manifest: {path.name}")
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(f"cannot read {path.name}: {type(exc).__name__}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{path.name} must contain a mapping")
        return {}
    return payload


def _missing_fields(record: dict[str, Any], fields: set[str]) -> list[str]:
    return sorted(field for field in fields if record.get(field) in (None, "", []))


def _source_registry(payload: dict[str, Any], errors: list[str]) -> dict[str, dict[str, Any]]:
    sources = payload.get("sources")
    if not isinstance(sources, list):
        errors.append("sources.yaml sources must be a list")
        return {}

    registry: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        label = f"source[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be a mapping")
            continue
        missing = _missing_fields(source, _SOURCE_FIELDS)
        if missing:
            errors.append(f"{label} missing fields: {', '.join(missing)}")
            continue
        source_id = str(source["id"])
        if source_id in registry:
            errors.append(f"duplicate source id: {source_id}")
            continue
        if _DISCOVERY_ONLY_MARKER in str(source["url"]).casefold():
            errors.append(f"source {source_id} is a discovery-only repository")
        if source["commercial_allowed"] is not True:
            errors.append(f"source {source_id} is not approved for commercial use")
        registry[source_id] = source
    return registry


def _validate_item(
    item: object,
    index: int,
    root: Path,
    sources: dict[str, dict[str, Any]],
    seen_ids: set[str],
) -> list[str]:
    label = f"item[{index}]"
    if not isinstance(item, dict):
        return [f"{label} must be a mapping"]

    errors: list[str] = []
    missing = _missing_fields(item, _ITEM_FIELDS)
    if missing:
        errors.append(f"{label} missing fields: {', '.join(missing)}")
        return errors

    item_id = str(item["id"])
    if item_id in seen_ids:
        errors.append(f"duplicate item id: {item_id}")
    seen_ids.add(item_id)

    if item["evidence_level"] not in _EVIDENCE_LEVELS:
        errors.append(f"{item_id} has invalid evidence_level")
    if item["creation_mode"] not in _CREATION_MODES:
        errors.append(f"{item_id} has invalid creation_mode")
    if item["commercial_allowed"] is not True:
        errors.append(f"{item_id} is not approved for commercial use")

    source_ids = item["source_ids"]
    if not isinstance(source_ids, list) or not all(isinstance(value, str) for value in source_ids):
        errors.append(f"{item_id} source_ids must be a list of strings")
    else:
        for source_id in source_ids:
            if source_id not in sources:
                errors.append(f"{item_id} references unknown source {source_id}")

    candidate = (root / str(item["path"])).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        errors.append(f"{item_id} path resolves outside repository")
    else:
        if not candidate.is_file():
            errors.append(f"{item_id} document is missing: {item['path']}")
    return errors


def validate_catalog(root: Path) -> CatalogReport:
    """Audit manifests and documents below *root* without mutating them."""

    repository_root = Path(root).expanduser().resolve()
    errors: list[str] = []
    source_payload = _load_mapping(repository_root / "knowledge" / "sources.yaml", errors)
    catalog_payload = _load_mapping(repository_root / "knowledge" / "catalog.yaml", errors)
    sources = _source_registry(source_payload, errors)

    items = catalog_payload.get("items")
    if not isinstance(items, list):
        errors.append("catalog.yaml items must be a list")
        items = []

    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        errors.extend(_validate_item(item, index, repository_root, sources, seen_ids))

    return CatalogReport(item_count=len(items), errors=tuple(sorted(errors)))
