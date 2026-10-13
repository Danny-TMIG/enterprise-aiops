"""RAMSubstrate — the fast in-memory head of the fabric.

Structure:
    RAMSubstrate
        .stream   -> StreamingSubstrate

Reads: served from RAM when the record is in the ring, else from the
durable ledger (data/fabric.sqlite3, table `events`).
Writes: appended to RAM ring and written through to the ledger in the
same call. Chain-hashed with the previous row's hash so the ledger
stays tamper-evident.
Restart: the ring is refilled from the last N rows of the ledger.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.core.streaming_substrate import StreamingSubstrate

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


@dataclass
class Event:
    seq: int
    kind: str
    subject: str
    payload: str
    prev_hash: str | None
    hash: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RAMSubstrate:
    """Bounded, thread-safe, RAM-resident head over the events ledger."""

    def __init__(self, *, capacity: int = 8192,
                 db_path: Path | None = None,
                 autoload: bool = True):
        self.capacity = capacity
        self.db_path = Path(db_path) if db_path else DB
        self._ring: deque[Event] = deque(maxlen=capacity)
        self._by_subject: dict[str, list[int]] = {}
        self._lock = threading.RLock()
        self._writes = 0
        self.stream = StreamingSubstrate()
        if autoload and self.db_path.exists():
            self._load_tail()

    # ── durability ────────────────────────────────────────────────
    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=10.0)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA busy_timeout=10000")
        con.execute("PRAGMA synchronous=NORMAL")
        return con

    def _load_tail(self) -> int:
        con = self._connect()
        rows = con.execute(
            "SELECT seq,kind,subject,payload,prev_hash,hash,created_at "
            "FROM events ORDER BY seq DESC LIMIT ?",
            (self.capacity,),
        ).fetchall()
        con.close()
        with self._lock:
            for r in reversed(rows):
                self._index(Event(*r))
        return len(rows)

    def _index(self, e: Event) -> None:
        self._ring.append(e)
        self._by_subject.setdefault(e.subject, []).append(e.seq)

    # ── write ─────────────────────────────────────────────────────
    def append(self, kind: str, subject: str, payload: Any) -> Event:
        with self._lock:
            con = self._connect()
            row = con.execute(
                "SELECT COALESCE(MAX(seq),0) FROM events").fetchone()
            seq = int(row[0]) + 1
            prev = con.execute(
                "SELECT hash FROM events ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            prev_hash = prev[0] if prev else None
            body = json.dumps(
                {"kind": kind, "subject": subject, "payload": payload},
                default=str, sort_keys=True,
            )
            h = hashlib.sha256(
                f"{prev_hash or ''}|{body}".encode()).hexdigest()
            con.execute(
                "INSERT INTO events "
                "(seq,kind,subject,payload,prev_hash,hash) VALUES (?,?,?,?,?,?)",
                (seq, kind, subject, body, prev_hash, h),
            )
            con.commit()
            created = con.execute(
                "SELECT created_at FROM events WHERE seq=?", (seq,)
            ).fetchone()[0]
            con.close()
            e = Event(seq, kind, subject, body, prev_hash, h, created)
            self._index(e)
            self._writes += 1
        self.stream.publish(kind, e.to_dict(),
                            meta={"subject": subject})
        return e

    # ── read ──────────────────────────────────────────────────────
    def tail(self, n: int = 50, *, kind: str | None = None) -> list[Event]:
        with self._lock:
            items = list(self._ring)
        if kind:
            items = [e for e in items if e.kind == kind]
        return items[-n:]

    def for_subject(self, subject: str, *, limit: int = 100) -> list[Event]:
        with self._lock:
            seqs = list(self._by_subject.get(subject, []))
        want = set(seqs[-limit:])
        with self._lock:
            return [e for e in self._ring if e.seq in want]

    def get(self, seq: int) -> Event | None:
        with self._lock:
            for e in self._ring:
                if e.seq == seq:
                    return e
        if not self.db_path.exists():
            return None
        con = self._connect()
        r = con.execute(
            "SELECT seq,kind,subject,payload,prev_hash,hash,created_at "
            "FROM events WHERE seq=?", (seq,)
        ).fetchone()
        con.close()
        return Event(*r) if r else None

    # ── verification ──────────────────────────────────────────────
    def verify_chain(self, *, from_seq: int = 1) -> dict[str, Any]:
        if not self.db_path.exists():
            return {"ok": False, "reason": "no ledger"}
        con = self._connect()
        prev = None
        if from_seq > 1:
            row = con.execute(
                "SELECT hash FROM events WHERE seq < ? ORDER BY seq DESC LIMIT 1",
                (from_seq,),
            ).fetchone()
            prev = row[0] if row else None
        checked = 0
        for r in con.execute(
            "SELECT seq,payload,prev_hash,hash "
            "FROM events WHERE seq>=? ORDER BY seq", (from_seq,)
        ):
            seq, payload, prev_hash, h = r
            if prev_hash != prev:
                con.close()
                return {"ok": False, "reason": "prev_hash mismatch",
                        "seq": seq, "expected": prev, "found": prev_hash}
            want = hashlib.sha256(
                f"{prev_hash or ''}|{payload}".encode()).hexdigest()
            if want != h:
                con.close()
                return {"ok": False, "reason": "hash mismatch",
                        "seq": seq, "expected": want, "found": h}
            prev = h
            checked += 1
        con.close()
        return {"ok": True, "checked": checked, "head": prev}

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "capacity": self.capacity,
                "resident": len(self._ring),
                "subjects": len(self._by_subject),
                "writes_since_boot": self._writes,
                "head_seq": self._ring[-1].seq if self._ring else 0,
                "head_hash": self._ring[-1].hash if self._ring else None,
                "stream": self.stream.stats(),
            }

    # ── restart-safe reconstruction ───────────────────────────────
    def reload(self) -> int:
        with self._lock:
            self._ring.clear()
            self._by_subject.clear()
        return self._load_tail()


__all__ = ["Event", "RAMSubstrate"]


# ── self-registration as capability `ram_substrate` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("ram_substrate")
    def _entry(*args, **kwargs):
        return {"module": "app.core.ram_substrate", "code": "ram_substrate"}


_self_register()
