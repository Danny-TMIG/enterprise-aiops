"""GOV-KRN-003 — decision and outcome correlation.

Correlates the decisions taken under a single correlation_id with the
outcome that was returned, so Govern can prove that what was decided is
what was carried out. Correlation does not transform a claim type into
another: an authorization decision and an execution result remain
distinct claims linked by the correlation.

Contract: contracts/canonical/decision-outcome-correlation.schema.json
Invariants:
  - a correlation record is append-only and never mutated
  - a correlation references at least one decision and at most one outcome
  - a correlation record's chain_hash covers its full field set
  - closing a correlation twice is rejected
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS correlations (
    correlation_id TEXT    PRIMARY KEY,
    opened_at      REAL    NOT NULL,
    closed_at      REAL,
    decision_refs  TEXT    NOT NULL,
    outcome_ref    TEXT,
    status         TEXT    NOT NULL,
    chain_hash     TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_corr_status ON correlations(status);
CREATE INDEX IF NOT EXISTS idx_corr_opened ON correlations(opened_at);
"""


class CorrelationError(Exception):
    """Raised on any invariant violation."""


class AlreadyClosedError(CorrelationError):
    """Raised when closing a correlation that is already closed."""


@dataclass(frozen=True)
class Correlation:
    correlation_id: str
    opened_at: float
    closed_at: float | None
    decision_refs: list[str]
    outcome_ref: str | None
    status: str
    chain_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "opened_at": self.opened_at,
            "closed_at": self.closed_at,
            "decision_refs": self.decision_refs,
            "outcome_ref": self.outcome_ref,
            "status": self.status,
            "chain_hash": self.chain_hash,
        }


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _chain_hash(record: dict[str, Any]) -> str:
    payload = _canonical({k: v for k, v in record.items() if k != "chain_hash"})
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CorrelationRegistry:
    """Append-only correlation of decisions to their outcomes."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._lock = threading.RLock()
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def open(
        self,
        correlation_id: str,
        decision_refs: list[str],
    ) -> Correlation:
        if not correlation_id:
            raise CorrelationError("correlation_id must be non-empty")
        if not decision_refs:
            raise CorrelationError("at least one decision_ref is required")

        with self._lock:
            cur = self._conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            try:
                existing = cur.execute(
                    "SELECT 1 FROM correlations WHERE correlation_id = ?",
                    (correlation_id,),
                ).fetchone()
                if existing:
                    raise CorrelationError(f"correlation {correlation_id} already opened")
                record = {
                    "correlation_id": correlation_id,
                    "opened_at": time.time(),
                    "closed_at": None,
                    "decision_refs": list(decision_refs),
                    "outcome_ref": None,
                    "status": "OPEN",
                }
                record["chain_hash"] = _chain_hash(record)
                cur.execute(
                    "INSERT INTO correlations"
                    " (correlation_id, opened_at, closed_at, decision_refs,"
                    "  outcome_ref, status, chain_hash)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        record["correlation_id"],
                        record["opened_at"],
                        record["closed_at"],
                        _canonical(record["decision_refs"]),
                        record["outcome_ref"],
                        record["status"],
                        record["chain_hash"],
                    ),
                )
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
        return Correlation(**record)

    def close_with_outcome(self, correlation_id: str, outcome_ref: str) -> Correlation:
        if not outcome_ref:
            raise CorrelationError("outcome_ref must be non-empty")
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            try:
                row = cur.execute(
                    "SELECT correlation_id, opened_at, closed_at, decision_refs,"
                    " outcome_ref, status, chain_hash"
                    " FROM correlations WHERE correlation_id = ?",
                    (correlation_id,),
                ).fetchone()
                if row is None:
                    raise CorrelationError(f"unknown correlation {correlation_id}")
                if row[5] == "CLOSED":
                    raise AlreadyClosedError(f"correlation {correlation_id} already closed")
                opened_record = {
                    "correlation_id": row[0],
                    "opened_at": row[1],
                    "closed_at": row[2],
                    "decision_refs": json.loads(row[3]),
                    "outcome_ref": row[4],
                    "status": row[5],
                }
                expected_open = _chain_hash(opened_record)
                if expected_open != row[6]:
                    raise CorrelationError("open record integrity mismatch")
                closed = {
                    "correlation_id": row[0],
                    "opened_at": row[1],
                    "closed_at": time.time(),
                    "decision_refs": json.loads(row[3]),
                    "outcome_ref": outcome_ref,
                    "status": "CLOSED",
                }
                closed["chain_hash"] = _chain_hash(closed)
                cur.execute(
                    "UPDATE correlations SET closed_at = ?, outcome_ref = ?,"
                    " status = ?, chain_hash = ? WHERE correlation_id = ?",
                    (
                        closed["closed_at"],
                        closed["outcome_ref"],
                        closed["status"],
                        closed["chain_hash"],
                        correlation_id,
                    ),
                )
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
        return Correlation(**closed)

    def get(self, correlation_id: str) -> Correlation:
        with self._lock:
            row = self._conn.execute(
                "SELECT correlation_id, opened_at, closed_at, decision_refs,"
                " outcome_ref, status, chain_hash FROM correlations"
                " WHERE correlation_id = ?",
                (correlation_id,),
            ).fetchone()
        if row is None:
            raise CorrelationError(f"unknown correlation {correlation_id}")
        return Correlation(
            correlation_id=row[0],
            opened_at=row[1],
            closed_at=row[2],
            decision_refs=json.loads(row[3]),
            outcome_ref=row[4],
            status=row[5],
            chain_hash=row[6],
        )

    def open_correlations(self) -> list[str]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT correlation_id FROM correlations WHERE status = 'OPEN' ORDER BY opened_at"
            ).fetchall()
        return [r[0] for r in rows]

    def verify(self, correlation_id: str) -> bool:
        c = self.get(correlation_id)
        record = {
            "correlation_id": c.correlation_id,
            "opened_at": c.opened_at,
            "closed_at": c.closed_at,
            "decision_refs": c.decision_refs,
            "outcome_ref": c.outcome_ref,
            "status": c.status,
        }
        return _chain_hash(record) == c.chain_hash
