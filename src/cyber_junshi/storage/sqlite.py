"""Transactional local SQLite persistence for explicit outcome records."""

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cyber_junshi.core.decision import create_action_plan, review_decision
from cyber_junshi.core.models import ActionPlan

_SCHEMA = """
CREATE TABLE IF NOT EXISTS outcomes (
    record_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    plan_json TEXT NOT NULL,
    observed_signals_json TEXT NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class DecisionStore:
    """Store only outcomes explicitly submitted by a caller."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _normalize_signals(observed_signals: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for signal in observed_signals:
            if not isinstance(signal, str):
                raise ValueError("observed_signals entries must be strings")
            item = " ".join(signal.split())
            if item and item not in seen:
                seen.add(item)
                normalized.append(item)
        return normalized

    def record_outcome(
        self,
        case_id: str,
        plan: ActionPlan,
        observed_signals: list[str],
        note: str = "",
    ) -> str:
        """Persist a decision outcome and return its opaque local identifier."""

        normalized_case_id = " ".join(case_id.split()) if isinstance(case_id, str) else ""
        if not normalized_case_id:
            raise ValueError("case_id must be a non-empty string")
        if not isinstance(plan, ActionPlan):
            raise ValueError("plan must be an ActionPlan")
        if not isinstance(observed_signals, list):
            raise ValueError("observed_signals must be a list")
        if not isinstance(note, str):
            raise ValueError("note must be a string")

        normalized_signals = self._normalize_signals(observed_signals)
        review_decision(plan, normalized_signals)
        record_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        plan_json = json.dumps(asdict(plan), ensure_ascii=False, separators=(",", ":"))
        signals_json = json.dumps(normalized_signals, ensure_ascii=False, separators=(",", ":"))

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO outcomes (
                    record_id, case_id, plan_json, observed_signals_json, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    normalized_case_id,
                    plan_json,
                    signals_json,
                    note.strip(),
                    created_at,
                ),
            )
        return record_id

    def review_decision(self, record_id: str) -> dict[str, object]:
        """Load a stored outcome and evaluate it with the current pure reviewer."""

        normalized_record_id = (
            " ".join(record_id.split()) if isinstance(record_id, str) else ""
        )
        if not normalized_record_id:
            raise ValueError("record_id must be a non-empty string")

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT record_id, case_id, plan_json, observed_signals_json, note, created_at
                FROM outcomes WHERE record_id = ?
                """,
                (normalized_record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown outcome record: {normalized_record_id}")

        plan_data = json.loads(row["plan_json"])
        observed_signals = json.loads(row["observed_signals_json"])
        plan = create_action_plan(
            action=plan_data["action"],
            observation_hours=plan_data["observation_hours"],
            success_signals=plan_data["success_signals"],
            downgrade_signals=plan_data["downgrade_signals"],
            stop_signals=plan_data["stop_signals"],
        )
        status = review_decision(plan, observed_signals)
        return {
            "record_id": row["record_id"],
            "case_id": row["case_id"],
            "plan": asdict(plan),
            "observed_signals": observed_signals,
            "status": status.value,
            "note": row["note"],
            "created_at": row["created_at"],
        }
