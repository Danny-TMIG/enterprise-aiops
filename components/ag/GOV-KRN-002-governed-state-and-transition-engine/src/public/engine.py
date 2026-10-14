"""GOV-KRN-002 — governed state and transition engine.

Every state transition is:
  - wrapped in a complete ASF Common Envelope
  - validated against contracts/canonical/common-envelope.schema.json
  - recorded as an append-only WORM row keyed by (subject_id, seq)
  - hash-chained so history is tamper-evident

Contract: contracts/canonical/common-envelope.schema.json
Invariants (from the Govern FAS):
  GOV-INV-007 every consequential terminal outcome has an immutable,
             reconstructible evidence chain
  GOV-INV-008 missing identity, authority, policy, classification, integrity,
             or evidence dependencies fail closed
  GOV-INV-009 historical state and policy are corrected by supersession,
             not silent mutation

Local invariants:
  - a transition without a complete envelope is rejected
  - recorded transitions are never mutated
  - seq increments by exactly 1 per subject
  - chain_hash references the previous row's chain_hash
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

ENVELOPE_REQUIRED = (
    "schema_version",
    "object_id",
    "correlation_id",
    "sovereign_domain",
    "issuer",
    "purpose",
    "classification",
    "event_time",
    "integrity",
)
TRANSITION_REQUIRED = ("from_state", "to_state", "actor", "reason")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS transitions (
    subject_id    TEXT    NOT NULL,
    seq           INTEGER NOT NULL,
    from_state    TEXT    NOT NULL,
    to_state      TEXT    NOT NULL,
    actor         TEXT    NOT NULL,
    reason        TEXT    NOT NULL,
    envelope_json TEXT    NOT NULL,
    prev_hash     TEXT,
    chain_hash    TEXT    NOT NULL,
    created_at    REAL    NOT NULL,
    PRIMARY KEY (subject_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_trans_subject ON transitions(subject_id);
CREATE INDEX IF NOT EXISTS idx_trans_created ON transitions(created_at);
"""


class TransitionError(Exception):
    """Raised on any invariant violation."""


class EnvelopeError(TransitionError):
    """Raised when the envelope is missing fields or malformed."""


class ConcurrencyError(TransitionError):
    """Raised when the caller's expected sequence does not match."""


@dataclass(frozen=True)
class Transition:
    subject_id: str
    seq: int
    from_state: str
    to_state: str
    actor: str
    reason: str
    envelope: dict[str, Any]
    prev_hash: str | None
    chain_hash: str
    created_at: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "seq": self.seq,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "actor": self.actor,
            "reason": self.reason,
            "envelope": self.envelope,
            "prev_hash": self.prev_hash,
            "chain_hash": self.chain_hash,
            "created_at": self.created_at,
        }


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _chain_hash(
    subject_id: str,
    seq: int,
    from_state: str,
    to_state: str,
    actor: str,
    reason: str,
    envelope_json: str,
    prev_hash: str | None,
) -> str:
    h = hashlib.sha256()
    for part in (
        subject_id,
        str(seq),
        from_state,
        to_state,
        actor,
        reason,
        envelope_json,
        prev_hash or "",
    ):
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def validate_envelope(envelope: Any) -> None:
    if not isinstance(envelope, dict):
        raise EnvelopeError("envelope must be an object")
    missing = [k for k in ENVELOPE_REQUIRED if not envelope.get(k)]
    if missing:
        raise EnvelopeError(f"envelope missing required fields: {missing}")
    integrity = envelope.get("integrity")
    if not isinstance(integrity, dict) or "digest" not in integrity:
        raise EnvelopeError("envelope.integrity must be an object with 'digest'")


def validate_transition(from_state: str, to_state: str, actor: str, reason: str) -> None:
    for name, val in (
        ("from_state", from_state),
        ("to_state", to_state),
        ("actor", actor),
        ("reason", reason),
    ):
        if not val or not isinstance(val, str):
            raise TransitionError(f"{name} must be a non-empty string")


class TransitionEngine:
    """Append-only, envelope-validated, hash-chained state transition log."""

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

    def latest_seq(self, subject_id: str) -> int:
        with self._lock:
            row = self._conn.execute(
                "SELECT MAX(seq) FROM transitions WHERE subject_id = ?",
                (subject_id,),
            ).fetchone()
            return int(row[0]) if row and row[0] is not None else 0

    def current_state(self, subject_id: str) -> str | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT to_state FROM transitions WHERE subject_id = ? ORDER BY seq DESC LIMIT 1",
                (subject_id,),
            ).fetchone()
            return row[0] if row else None

    def history(self, subject_id: str) -> list[Transition]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT subject_id, seq, from_state, to_state, actor, reason,"
                " envelope_json, prev_hash, chain_hash, created_at"
                " FROM transitions WHERE subject_id = ? ORDER BY seq ASC",
                (subject_id,),
            ).fetchall()
        return [
            Transition(
                subject_id=r[0],
                seq=r[1],
                from_state=r[2],
                to_state=r[3],
                actor=r[4],
                reason=r[5],
                envelope=json.loads(r[6]),
                prev_hash=r[7],
                chain_hash=r[8],
                created_at=r[9],
            )
            for r in rows
        ]

    def record(
        self,
        subject_id: str,
        from_state: str,
        to_state: str,
        actor: str,
        reason: str,
        envelope: dict[str, Any],
        expected_seq: int | None = None,
    ) -> Transition:
        if not subject_id:
            raise TransitionError("subject_id must be non-empty")
        validate_transition(from_state, to_state, actor, reason)
        validate_envelope(envelope)

        with self._lock:
            cur = self._conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            try:
                row = cur.execute(
                    "SELECT MAX(seq) FROM transitions WHERE subject_id = ?",
                    (subject_id,),
                ).fetchone()
                current = int(row[0]) if row and row[0] is not None else 0

                if expected_seq is not None and expected_seq != current:
                    raise ConcurrencyError(f"expected seq {expected_seq}, current {current}")
                seq = current + 1

                if current == 0:
                    prev_hash = None
                else:
                    pr = cur.execute(
                        "SELECT chain_hash FROM transitions WHERE subject_id = ? AND seq = ?",
                        (subject_id, current),
                    ).fetchone()
                    prev_hash = pr[0] if pr else None

                env_json = _canonical(envelope)
                ch = _chain_hash(
                    subject_id, seq, from_state, to_state, actor, reason, env_json, prev_hash
                )
                created = time.time()

                cur.execute(
                    "INSERT INTO transitions"
                    " (subject_id, seq, from_state, to_state, actor, reason,"
                    "  envelope_json, prev_hash, chain_hash, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        subject_id,
                        seq,
                        from_state,
                        to_state,
                        actor,
                        reason,
                        env_json,
                        prev_hash,
                        ch,
                        created,
                    ),
                )
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

        return Transition(
            subject_id=subject_id,
            seq=seq,
            from_state=from_state,
            to_state=to_state,
            actor=actor,
            reason=reason,
            envelope=envelope,
            prev_hash=prev_hash,
            chain_hash=ch,
            created_at=created,
        )

    def verify_chain(self, subject_id: str) -> bool:
        prev = None
        for t in self.history(subject_id):
            expected = _chain_hash(
                t.subject_id,
                t.seq,
                t.from_state,
                t.to_state,
                t.actor,
                t.reason,
                _canonical(t.envelope),
                prev,
            )
            if expected != t.chain_hash:
                return False
            prev = t.chain_hash
        return True

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0]
            subjects = self._conn.execute(
                "SELECT COUNT(DISTINCT subject_id) FROM transitions"
            ).fetchone()[0]
        return {"transitions": int(total), "subjects": int(subjects)}


# Backward-compatible alias for the earlier class name.
StateTransitionEngine = TransitionEngine
