import sqlite3

import pytest

from cyber_junshi.core.decision import create_action_plan
from cyber_junshi.storage.sqlite import DecisionStore


def test_record_and_review_outcome_round_trip(tmp_path) -> None:
    store = DecisionStore(tmp_path / "nested" / "junshi.db")
    plan = create_action_plan(
        "等待一次明确回复",
        24,
        ["明确回复"],
        ["含糊回复"],
        ["拒绝联系"],
    )

    record_id = store.record_outcome(
        "case-demo-001", plan, ["明确回复"], "synthetic outcome"
    )
    review = store.review_decision(record_id)

    assert review["record_id"] == record_id
    assert review["case_id"] == "case-demo-001"
    assert review["status"] == "continue"
    assert review["note"] == "synthetic outcome"
    assert review["created_at"].endswith("Z")


def test_initialization_creates_parent_and_schema(tmp_path) -> None:
    database_path = tmp_path / "junshi.db"
    DecisionStore(database_path)

    with sqlite3.connect(database_path) as connection:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(outcomes)").fetchall()
        }

    assert database_path.is_file()
    assert columns == {
        "record_id",
        "case_id",
        "plan_json",
        "observed_signals_json",
        "note",
        "created_at",
    }


def test_review_rejects_unknown_record(tmp_path) -> None:
    store = DecisionStore(tmp_path / "junshi.db")

    with pytest.raises(KeyError, match="unknown outcome record"):
        store.review_decision("missing-record")


def test_record_rejects_blank_case_id_without_writing(tmp_path) -> None:
    store = DecisionStore(tmp_path / "junshi.db")
    plan = create_action_plan("观察", 24, ["回复"], [], ["拒绝"])

    with pytest.raises(ValueError, match="case_id"):
        store.record_outcome(" ", plan, ["回复"], "synthetic")

    with sqlite3.connect(store.path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM outcomes").fetchone()[0]
    assert count == 0
