"""Explicit, subject-isolated local memory backed by SQLite."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

_MEMORY_KINDS = {"fact", "inference", "unknown", "boundary", "preference", "event", "decision"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    subject_id TEXT PRIMARY KEY,
    alias TEXT NOT NULL,
    alias_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    archived_at TEXT
);

CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_items (
    memory_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (
        kind IN ('fact', 'inference', 'unknown', 'boundary', 'preference', 'event', 'decision')
    ),
    content TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    source_question_id TEXT NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('active', 'superseded', 'deleted')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_questions_subject_created
ON questions(subject_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_memory_subject_status
ON memory_items(subject_id, status, created_at DESC);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _required_text(value: object, field: str) -> str:
    normalized = " ".join(value.split()) if isinstance(value, str) else ""
    if not normalized:
        raise ValueError(f"{field} must be a non-empty string")
    return normalized


def _validate_memories(memories: object) -> list[dict[str, object]]:
    if not isinstance(memories, list):
        raise ValueError("memories must be a list")
    normalized: list[dict[str, object]] = []
    for memory in memories:
        if not isinstance(memory, dict):
            raise ValueError("each memory must be a mapping")
        kind = memory.get("kind")
        if kind not in _MEMORY_KINDS:
            raise ValueError(f"memory kind must be one of {sorted(_MEMORY_KINDS)}")
        content = _required_text(memory.get("content"), "memory content")
        confidence = memory.get("confidence", 0.5)
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ValueError("memory confidence must be a number from 0 to 1")
        numeric_confidence = float(confidence)
        if not 0.0 <= numeric_confidence <= 1.0:
            raise ValueError("memory confidence must be from 0 to 1")
        normalized.append(
            {"kind": str(kind), "content": content, "confidence": numeric_confidence}
        )
    return normalized


class SubjectMemoryStore:
    """Persist only questions and memory explicitly submitted by the caller."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _alias_parts(subject_alias: object) -> tuple[str, str]:
        alias = _required_text(subject_alias, "subject_alias")
        return alias, alias.casefold()

    def remember_question(
        self,
        subject_alias: str,
        question_text: str,
        summary: str,
        memories: list[dict[str, object]],
    ) -> dict[str, object]:
        """Explicitly store one question and optional memory items for one subject."""

        alias, alias_key = self._alias_parts(subject_alias)
        normalized_question = _required_text(question_text, "question_text")
        normalized_summary = _required_text(summary, "summary")
        normalized_memories = _validate_memories(memories)
        now = _utc_now()
        question_id = str(uuid4())
        memory_ids = [str(uuid4()) for _ in normalized_memories]

        with self._connect() as connection:
            row = connection.execute(
                "SELECT subject_id FROM subjects WHERE alias_key = ?",
                (alias_key,),
            ).fetchone()
            if row is None:
                subject_id = str(uuid4())
                connection.execute(
                    """
                    INSERT INTO subjects (
                        subject_id, alias, alias_key, created_at, updated_at, archived_at
                    ) VALUES (?, ?, ?, ?, ?, NULL)
                    """,
                    (subject_id, alias, alias_key, now, now),
                )
            else:
                subject_id = str(row["subject_id"])
                connection.execute(
                    "UPDATE subjects SET updated_at = ?, archived_at = NULL WHERE subject_id = ?",
                    (now, subject_id),
                )

            connection.execute(
                """
                INSERT INTO questions (question_id, subject_id, question_text, summary, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (question_id, subject_id, normalized_question, normalized_summary, now),
            )
            connection.executemany(
                """
                INSERT INTO memory_items (
                    memory_id, subject_id, kind, content, confidence,
                    source_question_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?)
                """,
                [
                    (
                        memory_id,
                        subject_id,
                        memory["kind"],
                        memory["content"],
                        memory["confidence"],
                        question_id,
                        now,
                        now,
                    )
                    for memory_id, memory in zip(memory_ids, normalized_memories, strict=True)
                ],
            )
        return {
            "subject_id": subject_id,
            "question_id": question_id,
            "memory_ids": memory_ids,
            "database": str(self.path),
        }

    def _subject_row(self, connection: sqlite3.Connection, subject_alias: str) -> sqlite3.Row:
        _, alias_key = self._alias_parts(subject_alias)
        row = connection.execute(
            """
            SELECT subject_id, alias, created_at, updated_at
            FROM subjects WHERE alias_key = ? AND archived_at IS NULL
            """,
            (alias_key,),
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown subject: {subject_alias}")
        return row

    def recall_subject(self, subject_alias: str, limit: int = 10) -> dict[str, object]:
        """Recall recent questions and active memory for exactly one subject."""

        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer from 1 to 100")
        with self._connect() as connection:
            subject = self._subject_row(connection, subject_alias)
            questions = connection.execute(
                """
                SELECT question_id, question_text, summary, created_at
                FROM questions WHERE subject_id = ?
                ORDER BY created_at DESC, rowid DESC LIMIT ?
                """,
                (subject["subject_id"], limit),
            ).fetchall()
            memory_items = connection.execute(
                """
                SELECT memory_id, kind, content, confidence, source_question_id,
                       status, created_at, updated_at
                FROM memory_items
                WHERE subject_id = ? AND status = 'active'
                ORDER BY created_at DESC, rowid DESC
                """,
                (subject["subject_id"],),
            ).fetchall()
        return {
            "subject_id": subject["subject_id"],
            "alias": subject["alias"],
            "created_at": subject["created_at"],
            "updated_at": subject["updated_at"],
            "questions": [dict(row) for row in questions],
            "memory_items": [dict(row) for row in memory_items],
        }

    def list_subjects(self, include_archived: bool = False) -> list[dict[str, Any]]:
        """List subject metadata and counts without returning question text."""

        if not isinstance(include_archived, bool):
            raise ValueError("include_archived must be a boolean")
        condition = "" if include_archived else "WHERE s.archived_at IS NULL"
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT s.subject_id, s.alias, s.created_at, s.updated_at, s.archived_at,
                       COUNT(DISTINCT q.question_id) AS question_count,
                       COUNT(DISTINCT m.memory_id) AS memory_count
                FROM subjects AS s
                LEFT JOIN questions AS q ON q.subject_id = s.subject_id
                LEFT JOIN memory_items AS m
                    ON m.subject_id = s.subject_id AND m.status = 'active'
                {condition}
                GROUP BY s.subject_id
                ORDER BY s.updated_at DESC, s.rowid DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def forget_subject(self, subject_alias: str, confirm: bool = False) -> dict[str, int]:
        """Hard-delete one subject and all linked local memory after confirmation."""

        if confirm is not True:
            raise ValueError("confirm must be true to permanently forget a subject")
        with self._connect() as connection:
            subject = self._subject_row(connection, subject_alias)
            subject_id = subject["subject_id"]
            question_count = connection.execute(
                "SELECT COUNT(*) FROM questions WHERE subject_id = ?", (subject_id,)
            ).fetchone()[0]
            memory_count = connection.execute(
                "SELECT COUNT(*) FROM memory_items WHERE subject_id = ?", (subject_id,)
            ).fetchone()[0]
            connection.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id,))
        return {"subjects": 1, "questions": question_count, "memory_items": memory_count}
