from pathlib import Path

import pytest

from cyber_junshi.knowledge.search import search_knowledge

ROOT = Path(__file__).resolve().parents[2]


def test_search_finds_relevant_independent_knowledge() -> None:
    results = search_knowledge("网络约会诈骗", root=ROOT)

    assert results[0]["id"] == "core-09"
    assert results[0]["evidence_level"] == "E1"
    assert "诈骗" in results[0]["excerpt"]
    assert results[0]["source_ids"] == ["ftc-romance-scams", "project-four-mechanisms"]


def test_search_can_find_practical_card_and_respects_limit() -> None:
    results = search_knowledge("拒绝", limit=1, root=ROOT)

    assert len(results) == 1
    assert results[0]["id"] == "practical-14"


@pytest.mark.parametrize(("query", "limit"), [(" ", 5), ("consent", 0), ("consent", 21)])
def test_search_rejects_invalid_input(query: str, limit: int) -> None:
    with pytest.raises(ValueError):
        search_knowledge(query, limit=limit, root=ROOT)
