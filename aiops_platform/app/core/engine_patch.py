from __future__ import annotations
import hashlib, json, time
from dataclasses import dataclass, field, asdict

@dataclass
class PatchRecord:
    name: str
    version: str = "1.0.0"
    applied_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    payload: dict = field(default_factory=dict)
    def digest(self) -> str:
        canon = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canon.encode()).hexdigest()

class SovereignEnginePatch:
    def __init__(self) -> None:
        self._applied: list[PatchRecord] = []
    def apply(self, name: str, payload: dict | None = None) -> PatchRecord:
        rec = PatchRecord(name=name, payload=payload or {})
        self._applied.append(rec)
        return rec
    def history(self) -> list[PatchRecord]:
        return list(self._applied)
    def merkle_root(self) -> str:
        if not self._applied:
            return hashlib.sha256(b"empty").hexdigest()
        h = hashlib.sha256()
        for r in self._applied:
            h.update(r.digest().encode())
        return h.hexdigest()
