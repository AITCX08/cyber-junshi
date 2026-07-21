import sqlite3
from pathlib import Path

import pytest

from cyber_junshi.storage.memory import SubjectMemoryStore


def test_remember_and_recall_question_with_memory_items(tmp_path: Path) -> None:
    store = SubjectMemoryStore(tmp_path / "nested" / "memory.db")

    saved = store.remember_question(
        "对象甲",
        "  对方连续两次取消见面，我该继续问吗？  ",
        "连续两次取消见面",
        [
            {"kind": "fact", "content": "两次约见均被取消", "confidence": 1.0},
            {"kind": "unknown", "content": "取消的具体原因", "confidence": 0.2},
        ],
    )
    recalled = store.recall_subject("对象甲")

    assert saved["subject_id"] == recalled["subject_id"]
    assert recalled["alias"] == "对象甲"
    assert recalled["questions"][0]["question_text"] == "对方连续两次取消见面，我该继续问吗？"
    assert recalled["questions"][0]["summary"] == "连续两次取消见面"
    assert {item["kind"] for item in recalled["memory_items"]} == {"fact", "unknown"}


def test_normalized_alias_reuses_one_subject(tmp_path: Path) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")

    first = store.remember_question("  Person A ", "first question", "first", [])
    second = store.remember_question("person a", "second question", "second", [])

    assert first["subject_id"] == second["subject_id"]
    assert len(store.list_subjects()) == 1


def test_recall_is_strictly_isolated_by_subject(tmp_path: Path) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")
    store.remember_question(
        "对象甲", "甲的问题", "甲摘要", [{"kind": "fact", "content": "甲事实"}]
    )
    store.remember_question(
        "对象乙", "乙的问题", "乙摘要", [{"kind": "fact", "content": "乙事实"}]
    )

    recalled = store.recall_subject("对象甲")

    assert [question["summary"] for question in recalled["questions"]] == ["甲摘要"]
    assert [item["content"] for item in recalled["memory_items"]] == ["甲事实"]
    assert "乙" not in str(recalled)


def test_recall_returns_newest_questions_up_to_limit(tmp_path: Path) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")
    store.remember_question("对象甲", "question one", "one", [])
    store.remember_question("对象甲", "question two", "two", [])

    recalled = store.recall_subject("对象甲", limit=1)

    assert [question["summary"] for question in recalled["questions"]] == ["two"]


@pytest.mark.parametrize(
    ("memory", "message"),
    [
        ({"kind": "diagnosis", "content": "label"}, "kind"),
        ({"kind": "fact", "content": "value", "confidence": 1.1}, "confidence"),
        ({"kind": "fact", "content": " "}, "content"),
    ],
)
def test_invalid_memory_item_is_rejected_without_partial_write(
    tmp_path: Path, memory: dict[str, object], message: str
) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")

    with pytest.raises(ValueError, match=message):
        store.remember_question("对象甲", "question", "summary", [memory])

    assert store.list_subjects() == []


@pytest.mark.parametrize(
    ("alias", "question", "summary", "message"),
    [
        (" ", "question", "summary", "subject_alias"),
        ("person", " ", "summary", "question_text"),
        ("person", "question", " ", "summary"),
    ],
)
def test_blank_required_text_is_rejected(
    tmp_path: Path, alias: str, question: str, summary: str, message: str
) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")

    with pytest.raises(ValueError, match=message):
        store.remember_question(alias, question, summary, [])


def test_list_subjects_reports_counts_without_question_text(tmp_path: Path) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")
    store.remember_question(
        "对象甲", "private question", "short summary", [{"kind": "fact", "content": "fact"}]
    )

    subjects = store.list_subjects()

    assert subjects[0]["alias"] == "对象甲"
    assert subjects[0]["question_count"] == 1
    assert subjects[0]["memory_count"] == 1
    assert "private question" not in str(subjects)


def test_forget_requires_confirmation_and_cascades(tmp_path: Path) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")
    store.remember_question(
        "对象甲", "question", "summary", [{"kind": "boundary", "content": "不再追问"}]
    )

    with pytest.raises(ValueError, match="confirm"):
        store.forget_subject("对象甲")

    deleted = store.forget_subject("对象甲", confirm=True)

    assert deleted == {"subjects": 1, "questions": 1, "memory_items": 1}
    with pytest.raises(KeyError, match="unknown subject"):
        store.recall_subject("对象甲")
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM memory_items").fetchone()[0] == 0


def test_recall_rejects_invalid_limit(tmp_path: Path) -> None:
    store = SubjectMemoryStore(tmp_path / "memory.db")

    with pytest.raises(ValueError, match="limit"):
        store.recall_subject("对象甲", limit=0)
