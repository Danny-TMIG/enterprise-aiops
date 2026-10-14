"""GOV-KRN-002: Governed state and transition engine (sqlite-backed)."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


class TransitionError(Exception): ...
class EnvelopeError(TransitionError): ...
class ConcurrencyError(TransitionError): ...

IncompleteEnvelopeError = EnvelopeError
StaleSeqError = ConcurrencyError

REQUIRED_ENVELOPE_FIELDS = (
    "schema_version", "object_id", "correlation_id", "sovereign_domain",
    "issuer", "purpose", "classification", "event_time", "integrity",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(obj: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(obj)).hexdigest()


@dataclass(frozen=True)
class Transition:
    subject: str
    seq: int
    from_state: str
    to_state: str
    actor: str
    reason: str
    envelope: dict[str, Any]
    prev_hash: str | None
    chain_hash: str
    created_at: str


def _validate_envelope(env: dict[str, Any]) -> None:
    if not isinstance(env, dict):
        raise EnvelopeError("envelope must be a mapping")
    for name in REQUIRED_ENVELOPE_FIELDS:
        if name not in env or env[name] in (None, ""):
            raise EnvelopeError(f"missing envelope field: {name}")


class TransitionEngine:
    def __init__(self) -> None:
        self._conn = sqlite3.connect(":memory:")
        self._conn.execute(
            """
            CREATE TABLE transitions (
                subject_id  TEXT NOT NULL,
                seq         INTEGER NOT NULL,
                from_state  TEXT NOT NULL,
                to_state    TEXT NOT NULL,
                actor       TEXT NOT NULL,
                reason      TEXT NOT NULL,
                envelope_json TEXT NOT NULL,
                prev_hash   TEXT,
                chain_hash  TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                PRIMARY KEY (subject_id, seq)
            )
            """
        )
        self._conn.commit()

    def __enter__(self) -> "TransitionEngine":
        return self

    def __exit__(self, *exc: object) -> None:
        self._conn.close()

    def record(
        self,
        subject: str,
        from_state: str,
        to_state: str,
        actor: str,
        reason: str,
        envelope: dict[str, Any],
        expected_seq: int | None = None,
    ) -> Transition:
        if not subject:
            raise TransitionError("subject must be non-empty")
        _validate_envelope(envelope)

        cur = self._conn.execute(
            "SELECT COALESCE(MAX(seq), 0) FROM transitions WHERE subject_id = ?",
            (subject,),
        )
        current = cur.fetchone()[0]

        if expected_seq is not None and expected_seq != current:
            raise ConcurrencyError(f"expected seq {expected_seq}, current is {current}")

        prev_hash = None
        if current > 0:
            cur = self._conn.execute(
                "SELECT chain_hash FROM transitions WHERE subject_id = ? AND seq = ?",
                (subject, current),
            )
            prev_hash = cur.fetchone()[0]

        next_seq = current + 1
        created_at = _now()
        envelope_json = json.dumps(envelope, sort_keys=True)
        chain_hash = _hash({
            "subject_id": subject,
            "seq": next_seq,
            "from_state": from_state,
            "to_state": to_state,
            "actor": actor,
            "reason": reason,
            "envelope_json": envelope_json,
            "prev_hash": prev_hash,
            "created_at": created_at,
        })

        self._conn.execute(
            "INSERT INTO transitions "
            "(subject_id, seq, from_state, to_state, actor, reason, envelope_json, prev_hash, chain_hash, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (subject, next_seq, from_state, to_state, actor, reason, envelope_json, prev_hash, chain_hash, created_at),
        )
        self._conn.commit()
        return Transition(subject, next_seq, from_state, to_state, actor, reason, envelope, prev_hash, chain_hash, created_at)

    def current_state(self, subject: str) -> str | None:
        cur = self._conn.execute(
            "SELECT to_state FROM transitions WHERE subject_id = ? ORDER BY seq DESC LIMIT 1",
            (subject,),
        )
        row = cur.fetchone()
        return row[0] if row else None

    def verify_chain(self, subject: str) -> bool:
        cur = self._conn.execute(
            "SELECT seq, from_state, to_state, actor, reason, envelope_json, prev_hash, chain_hash, created_at "
            "FROM transitions WHERE subject_id = ? ORDER BY seq ASC",
            (subject,),
        )
        rows = cur.fetchall()
        if not rows:
            raise TransitionError(f"unknown subject: {subject}")
        prev = None
        for seq, f, t, a, r, env_json, prev_hash, chain_hash, created_at in rows:
            expected = _hash({
                "subject_id": subject,
                "seq": seq,
                "from_state": f,
                "to_state": t,
                "actor": a,
                "reason": r,
                "envelope_json": env_json,
                "prev_hash": prev_hash,
                "created_at": created_at,
            })
            if expected != chain_hash or prev_hash != prev:
                return False
            prev = chain_hash
        return True
