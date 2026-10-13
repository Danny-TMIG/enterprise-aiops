"""Source module for 35_CLOUD."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Record:
    """One immutable unit of work emitted by 35_CLOUD."""
    name: str
    payload: dict = field(default_factory=dict)
    ts: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def digest(self) -> str:
        canon = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canon.encode()).hexdigest()


class 35Cloud:
    """Primary interface for 35_CLOUD. Stateless, deterministic."""

    def __init__(self) -> None:
        self._records: list[Record] = []

    def emit(self, name: str, payload: dict | None = None) -> Record:
        rec = Record(name=name, payload=payload or {})
        self._records.append(rec)
        return rec

    def records(self) -> list[Record]:
        return list(self._records)

    def merkle_root(self) -> str:
        if not self._records:
            return hashlib.sha256(b"empty").hexdigest()
        h = hashlib.sha256()
        for r in self._records:
            h.update(r.digest().encode())
        return h.hexdigest()


__all__ = ["Record", "35Cloud"]
