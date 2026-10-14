"""GOV-FED-001 — Federation Gateway and Domain Exchange Coordinator.

Layer: ag   Group: Federation and Domain Exchange

Invariants:
  - GOV-INV-001 Cognition cannot authorize its own consequential action.
  - GOV-INV-002 Govern cannot execute a physical workload or represent scheduling as authority.
  - GOV-INV-003 Compute cannot broaden an execution order, select an unauthorized capability, or reinterpret policy.
  - GOV-INV-004 Authority, delegation, consent, and approval are bounded, attributable, time-aware, and revocable.
  - GOV-INV-005 Information movement and release require an explicit decision; transformation cannot increase authority.
  - GOV-INV-006 Mandatory constraints determine eligibility before optimization or convenience.

This module is generated to a working baseline: it stores its records,
enforces the shape of its inputs, and returns typed results. Interface
decisions reserved by the FAS are applied per the decisions workbook.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _seal(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()



SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS records (
    record_id   TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,
    payload     TEXT NOT NULL,
    seal        TEXT NOT NULL,
    created_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_records_kind ON records(kind);
"""


class Fed001Error(Exception):
    """Raised on invariant violation."""


class Fed001:
    """Federation Gateway and Domain Exchange Coordinator — functional baseline.

    Owns an append-only record store. Writes seal each record; reads
    return typed results; duplicate ids are rejected.
    """

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

    def __enter__(self) -> "Fed001":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def record(self, kind: str, payload: Dict[str, Any],
               record_id: Optional[str] = None) -> Dict[str, Any]:
        if not kind:
            raise Fed001Error("kind required")
        if not isinstance(payload, dict):
            raise Fed001Error("payload must be an object")
        rid = record_id or f"rec-{uuid.uuid4().hex[:12]}"
        record = {
            "record_id": rid,
            "kind": kind,
            "payload": payload,
            "created_at": time.time(),
        }
        record["seal"] = _seal(record)
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO records (record_id, kind, payload, seal, created_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (rid, kind, _canonical(payload), record["seal"],
                     record["created_at"]),
                )
                self._conn.commit()
            except sqlite3.IntegrityError:
                raise Fed001Error(f"record {rid} already exists")
        return record

    def get(self, record_id: str) -> Dict[str, Any]:
        with self._lock:
            row = self._conn.execute(
                "SELECT record_id, kind, payload, seal, created_at"
                " FROM records WHERE record_id = ?", (record_id,),
            ).fetchone()
        if row is None:
            raise Fed001Error(f"unknown record {record_id}")
        return {
            "record_id": row[0], "kind": row[1],
            "payload": json.loads(row[2]), "seal": row[3],
            "created_at": row[4],
        }

    def by_kind(self, kind: str) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT record_id, kind, payload, seal, created_at"
                " FROM records WHERE kind = ? ORDER BY created_at", (kind,),
            ).fetchall()
        return [{"record_id": r[0], "kind": r[1], "payload": json.loads(r[2]),
                  "seal": r[3], "created_at": r[4]} for r in rows]

    def verify(self, record_id: str) -> bool:
        rec = self.get(record_id)
        check = {k: v for k, v in rec.items() if k != "seal"}
        return _seal(check) == rec["seal"]

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
            kinds = self._conn.execute(
                "SELECT kind, COUNT(*) FROM records GROUP BY kind"
            ).fetchall()
        return {"records": int(total), "kinds": {k: int(c) for k, c in kinds}}
