"""GOV-KRN-001: Governance object model and registry (sqlite-backed)."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


class RegistryError(Exception): ...
class UnknownObjectError(RegistryError): ...
class ImmutableVersionError(RegistryError): ...

StaleVersionError = ImmutableVersionError


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(obj: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


@dataclass(frozen=True)
class Version:
    object_id: str
    version: int
    kind: str
    payload: dict[str, Any]
    prev_hash: str | None
    chain_hash: str
    created_at: str


class GovernanceRegistry:
    def __init__(self) -> None:
        self._conn = sqlite3.connect(":memory:")
        self._conn.execute(
            """
            CREATE TABLE governance_objects (
                object_id   TEXT NOT NULL,
                version     INTEGER NOT NULL,
                kind        TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                prev_hash   TEXT,
                chain_hash  TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                PRIMARY KEY (object_id, version)
            )
            """
        )
        self._conn.commit()

    def __enter__(self) -> "GovernanceRegistry":
        return self

    def __exit__(self, *exc: object) -> None:
        self._conn.close()

    def put(
        self,
        object_id: str,
        kind: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> Version:
        cur = self._conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM governance_objects WHERE object_id = ?",
            (object_id,),
        )
        current = cur.fetchone()[0]

        if expected_version is not None and expected_version != current:
            raise ImmutableVersionError(
                f"expected version {expected_version}, current is {current}"
            )

        prev_hash = None
        if current > 0:
            cur = self._conn.execute(
                "SELECT chain_hash FROM governance_objects WHERE object_id = ? AND version = ?",
                (object_id, current),
            )
            prev_hash = cur.fetchone()[0]

        next_version = current + 1
        created_at = _now()
        payload_json = json.dumps(payload, sort_keys=True)
        chain_hash = _hash({
            "object_id": object_id,
            "version": next_version,
            "kind": kind,
            "payload_json": payload_json,
            "prev_hash": prev_hash,
            "created_at": created_at,
        })

        self._conn.execute(
            "INSERT INTO governance_objects "
            "(object_id, version, kind, payload_json, prev_hash, chain_hash, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (object_id, next_version, kind, payload_json, prev_hash, chain_hash, created_at),
        )
        self._conn.commit()
        return Version(object_id, next_version, kind, payload, prev_hash, chain_hash, created_at)

    def get(self, object_id: str, version: int | None = None) -> Version:
        if version is None:
            cur = self._conn.execute(
                "SELECT version, kind, payload_json, prev_hash, chain_hash, created_at "
                "FROM governance_objects WHERE object_id = ? ORDER BY version DESC LIMIT 1",
                (object_id,),
            )
        else:
            cur = self._conn.execute(
                "SELECT version, kind, payload_json, prev_hash, chain_hash, created_at "
                "FROM governance_objects WHERE object_id = ? AND version = ?",
                (object_id, version),
            )
        row = cur.fetchone()
        if row is None:
            raise UnknownObjectError(f"unknown object: {object_id}")
        return Version(object_id, row[0], row[1], json.loads(row[2]), row[3], row[4], row[5])

    def list_ids(self, kind: str | None = None) -> list[str]:
        if kind is None:
            cur = self._conn.execute(
                "SELECT DISTINCT object_id FROM governance_objects ORDER BY object_id"
            )
        else:
            cur = self._conn.execute(
                "SELECT DISTINCT object_id FROM governance_objects WHERE kind = ? ORDER BY object_id",
                (kind,),
            )
        return [r[0] for r in cur.fetchall()]

    def verify_chain(self, object_id: str) -> bool:
        cur = self._conn.execute(
            "SELECT version, kind, payload_json, prev_hash, chain_hash, created_at "
            "FROM governance_objects WHERE object_id = ? ORDER BY version ASC",
            (object_id,),
        )
        rows = cur.fetchall()
        if not rows:
            raise UnknownObjectError(f"unknown object: {object_id}")
        prev = None
        for version, kind, payload_json, prev_hash, chain_hash, created_at in rows:
            expected = _hash({
                "object_id": object_id,
                "version": version,
                "kind": kind,
                "payload_json": payload_json,
                "prev_hash": prev_hash,
                "created_at": created_at,
            })
            if expected != chain_hash or prev_hash != prev:
                return False
            prev = chain_hash
        return True
