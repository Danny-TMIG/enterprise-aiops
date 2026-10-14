"""GOV-KRN-001 — governance object model and registry.

SQLite-backed, append-only registry of governance objects. Every object is
versioned. Versions are immutable: a new write to an existing object_id
produces a new version and never mutates an existing row. Each version row
carries a sha256 chain hash over (object_id, version, payload, prev_hash),
so the full history is tamper-evident.

Contract: contracts/gov/object_model_v1.json
Invariants:
  - an (object_id, version) pair is written at most once
  - a write to an existing object_id must increment version by exactly 1
  - the stored row is never updated in place
  - chain_hash of version N references chain_hash of version N-1
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS governance_objects (
    object_id     TEXT    NOT NULL,
    version       INTEGER NOT NULL,
    kind          TEXT    NOT NULL,
    payload_json  TEXT    NOT NULL,
    prev_hash     TEXT,
    chain_hash    TEXT    NOT NULL,
    created_at    REAL    NOT NULL,
    PRIMARY KEY (object_id, version)
);
CREATE INDEX IF NOT EXISTS idx_gov_kind ON governance_objects(kind);
CREATE INDEX IF NOT EXISTS idx_gov_created ON governance_objects(created_at);

CREATE TABLE IF NOT EXISTS registry_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class RegistryError(Exception):
    """Raised on any invariant violation."""


class ImmutableVersionError(RegistryError):
    """Raised when a write would mutate an existing version."""


class VersionGapError(RegistryError):
    """Raised when a new version is not exactly prev + 1."""


@dataclass(frozen=True)
class GovernanceObject:
    object_id: str
    version: int
    kind: str
    payload: dict[str, Any]
    prev_hash: str | None
    chain_hash: str
    created_at: float = field(default=0.0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "version": self.version,
            "kind": self.kind,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "chain_hash": self.chain_hash,
            "created_at": self.created_at,
        }


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _chain_hash(
    object_id: str,
    version: int,
    kind: str,
    payload_json: str,
    prev_hash: str | None,
) -> str:
    h = hashlib.sha256()
    h.update(object_id.encode("utf-8"))
    h.update(b"\x00")
    h.update(str(version).encode("utf-8"))
    h.update(b"\x00")
    h.update(kind.encode("utf-8"))
    h.update(b"\x00")
    h.update(payload_json.encode("utf-8"))
    h.update(b"\x00")
    h.update((prev_hash or "").encode("utf-8"))
    return h.hexdigest()


class GovernanceRegistry:
    """Append-only, versioned, hash-chained registry of governance objects."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._lock = threading.RLock()
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---- reads -----------------------------------------------------------

    def latest_version(self, object_id: str) -> int:
        with self._lock:
            row = self._conn.execute(
                "SELECT MAX(version) FROM governance_objects WHERE object_id = ?",
                (object_id,),
            ).fetchone()
            return int(row[0]) if row and row[0] is not None else 0

    def get(self, object_id: str, version: int | None = None) -> GovernanceObject:
        with self._lock:
            if version is None:
                version = self.latest_version(object_id)
                if version == 0:
                    raise RegistryError(f"unknown object_id: {object_id}")
            row = self._conn.execute(
                "SELECT object_id, version, kind, payload_json, prev_hash,"
                " chain_hash, created_at FROM governance_objects"
                " WHERE object_id = ? AND version = ?",
                (object_id, version),
            ).fetchone()
        if row is None:
            raise RegistryError(f"unknown object: {object_id} v{version}")
        return GovernanceObject(
            object_id=row[0],
            version=row[1],
            kind=row[2],
            payload=json.loads(row[3]),
            prev_hash=row[4],
            chain_hash=row[5],
            created_at=row[6],
        )

    def history(self, object_id: str) -> list[GovernanceObject]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT object_id, version, kind, payload_json, prev_hash,"
                " chain_hash, created_at FROM governance_objects"
                " WHERE object_id = ? ORDER BY version ASC",
                (object_id,),
            ).fetchall()
        return [
            GovernanceObject(
                object_id=r[0],
                version=r[1],
                kind=r[2],
                payload=json.loads(r[3]),
                prev_hash=r[4],
                chain_hash=r[5],
                created_at=r[6],
            )
            for r in rows
        ]

    def list_ids(self, kind: str | None = None) -> list[str]:
        with self._lock:
            if kind is None:
                rows = self._conn.execute(
                    "SELECT DISTINCT object_id FROM governance_objects ORDER BY object_id"
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT DISTINCT object_id FROM governance_objects"
                    " WHERE kind = ? ORDER BY object_id",
                    (kind,),
                ).fetchall()
        return [r[0] for r in rows]

    # ---- writes ----------------------------------------------------------

    def put(
        self,
        object_id: str,
        kind: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> GovernanceObject:
        """Append a new immutable version.

        expected_version enforces optimistic concurrency: pass the version you
        read, and the write fails if anyone else has advanced the chain.
        """
        if not object_id:
            raise RegistryError("object_id must be non-empty")
        if not kind:
            raise RegistryError("kind must be non-empty")
        if not isinstance(payload, dict):
            raise RegistryError("payload must be a JSON object")

        with self._lock:
            cur = self._conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            try:
                row = cur.execute(
                    "SELECT MAX(version) FROM governance_objects WHERE object_id = ?",
                    (object_id,),
                ).fetchone()
                current = int(row[0]) if row and row[0] is not None else 0

                if expected_version is not None and expected_version != current:
                    raise ImmutableVersionError(
                        f"concurrent modification: expected v{expected_version}, current v{current}"
                    )

                next_version = current + 1

                if current == 0:
                    prev_hash = None
                else:
                    prev_row = cur.execute(
                        "SELECT chain_hash FROM governance_objects"
                        " WHERE object_id = ? AND version = ?",
                        (object_id, current),
                    ).fetchone()
                    prev_hash = prev_row[0] if prev_row else None

                payload_json = _canonical(payload)
                ch = _chain_hash(object_id, next_version, kind, payload_json, prev_hash)
                created = time.time()

                cur.execute(
                    "INSERT INTO governance_objects"
                    " (object_id, version, kind, payload_json, prev_hash,"
                    "  chain_hash, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (object_id, next_version, kind, payload_json, prev_hash, ch, created),
                )
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

        return GovernanceObject(
            object_id=object_id,
            version=next_version,
            kind=kind,
            payload=payload,
            prev_hash=prev_hash,
            chain_hash=ch,
            created_at=created,
        )

    # ---- verification ----------------------------------------------------

    def verify_chain(self, object_id: str) -> bool:
        """Recompute every chain hash and confirm the links are intact."""
        prev = None
        for obj in self.history(object_id):
            expected = _chain_hash(
                obj.object_id,
                obj.version,
                obj.kind,
                _canonical(obj.payload),
                prev,
            )
            if expected != obj.chain_hash:
                return False
            prev = obj.chain_hash
        return True

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM governance_objects").fetchone()[0]
            objects = self._conn.execute(
                "SELECT COUNT(DISTINCT object_id) FROM governance_objects"
            ).fetchone()[0]
            kinds = self._conn.execute(
                "SELECT kind, COUNT(*) FROM governance_objects GROUP BY kind ORDER BY kind"
            ).fetchall()
        return {
            "versions": int(total),
            "objects": int(objects),
            "kinds": {k: int(c) for k, c in kinds},
        }
