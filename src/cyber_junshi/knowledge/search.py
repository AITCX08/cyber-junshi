"""Deterministic local search over the provenance-audited knowledge pack."""

import os
import re
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


def _required_query(value: object) -> str:
    query = " ".join(value.split()) if isinstance(value, str) else ""
    if not query:
        raise ValueError("query must be a non-empty string")
    return query


def _knowledge_directory(root: Path | None) -> tuple[Path, Path]:
    if root is not None:
        requested = Path(root).expanduser().resolve()
        knowledge = requested / "knowledge"
        if knowledge.is_dir():
            return knowledge, requested
        if (requested / "catalog.yaml").is_file():
            return requested, requested.parent
        raise FileNotFoundError(f"knowledge directory not found below {requested}")

    configured = os.environ.get("CYBER_JUNSHI_KNOWLEDGE")
    if configured:
        return _knowledge_directory(Path(configured))

    repository_root = Path(__file__).resolve().parents[3]
    if (repository_root / "knowledge" / "catalog.yaml").is_file():
        return repository_root / "knowledge", repository_root

    packaged = Path(__file__).resolve().parents[1] / "knowledge_data"
    if (packaged / "catalog.yaml").is_file():
        return packaged, packaged
    raise FileNotFoundError("packaged Cyber Junshi knowledge is unavailable")


def _load_items(knowledge: Path) -> list[dict[str, Any]]:
    payload = yaml.safe_load((knowledge / "catalog.yaml").read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("knowledge catalog must contain an items list")
    return [item for item in payload["items"] if isinstance(item, dict)]


def _document_path(item_path: object, knowledge: Path, document_base: Path) -> Path:
    relative = PurePosixPath(str(item_path))
    if knowledge.name == "knowledge_data" and relative.parts[:1] == ("knowledge",):
        relative = PurePosixPath(*relative.parts[1:])
        candidate = knowledge.joinpath(*relative.parts).resolve()
        base = knowledge.resolve()
    else:
        candidate = document_base.joinpath(*relative.parts).resolve()
        base = document_base.resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"knowledge path resolves outside base: {item_path}") from exc
    return candidate


def _search_terms(query: str) -> list[str]:
    normalized = query.casefold()
    terms = set(re.findall(r"[\w\u4e00-\u9fff]+", normalized))
    compact = "".join(normalized.split())
    if len(compact) >= 2:
        terms.update(compact[index : index + 2] for index in range(len(compact) - 1))
    return sorted(terms, key=lambda value: (-len(value), value))


def _excerpt(content: str, query: str, terms: list[str], length: int = 180) -> str:
    flattened = " ".join(content.replace("#", "").split())
    folded = flattened.casefold()
    positions = [folded.find(value) for value in [query.casefold(), *terms]]
    positions = [position for position in positions if position >= 0]
    start = max(0, min(positions, default=0) - 40)
    return flattened[start : start + length]


def search_knowledge(
    query: str,
    limit: int = 5,
    root: Path | None = None,
) -> list[dict[str, object]]:
    """Return ranked local knowledge excerpts with evidence and source identifiers."""

    normalized_query = _required_query(query)
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
        raise ValueError("limit must be an integer from 1 to 20")

    knowledge, document_base = _knowledge_directory(root)
    terms = _search_terms(normalized_query)
    ranked: list[tuple[int, str, dict[str, object]]] = []
    for item in _load_items(knowledge):
        path = _document_path(item.get("path"), knowledge, document_base)
        content = path.read_text(encoding="utf-8")
        title = content.splitlines()[0].lstrip("# ") if content.splitlines() else ""
        topic = str(item.get("topic", ""))
        title_folded = title.casefold()
        topic_folded = topic.casefold()
        content_folded = content.casefold()
        query_folded = normalized_query.casefold()
        score = 0
        if query_folded in title_folded:
            score += 200
        if query_folded in topic_folded:
            score += 160
        if query_folded in content_folded:
            score += 80
        for term in terms:
            score += title_folded.count(term) * 20
            score += topic_folded.count(term) * 12
            score += min(content_folded.count(term), 5) * 2
        if score == 0:
            continue
        result: dict[str, object] = {
            "id": str(item["id"]),
            "topic": topic,
            "evidence_level": str(item["evidence_level"]),
            "source_ids": list(item["source_ids"]),
            "excerpt": _excerpt(content, normalized_query, terms),
        }
        ranked.append((score, str(item["id"]), result))
    ranked.sort(key=lambda value: (-value[0], value[1]))
    return [result for _, _, result in ranked[:limit]]
