"""The backrooms: content-addressed residue store."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_DEFAULT = Path(".backrooms/entries.jsonl")
_LOCK = threading.Lock()


def _h(*p: str) -> str:
    m = hashlib.sha256()
    for s in p:
        m.update(s.encode("utf-8")); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()[:24]


@dataclass
class Entry:
    intent_hash: str
    residue: list[str]
    reason: str
    raw: str
    ts: str = field(default_factory=lambda: time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    @property
    def id(self) -> str:
        return _h("backroom", self.intent_hash, self.reason,
                  "|".join(sorted(self.residue)))


class Backrooms:
    def __init__(self, path: Path = _DEFAULT):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def store(self, e: Entry) -> str:
        with _LOCK, self.path.open("a") as f:
            f.write(json.dumps({**asdict(e), "id": e.id}) + "\n")
        return e.id

    def all(self) -> list[dict[str, Any]]:
        out = []
        for line in self.path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
        return out

    def search(self, substring: str) -> list[dict[str, Any]]:
        s = substring.lower()
        return [e for e in self.all()
                if s in e.get("raw", "").lower()
                or any(s in r.lower() for r in e.get("residue", []))]
