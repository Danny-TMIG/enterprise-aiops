"""Team coordination — quorum + epoch."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, List

def quorum(reports: Iterable[Hashable], *, strict: bool = True):
    counts = Counter(reports)
    if not counts: raise ValueError("no reports")
    win, n = counts.most_common(1)[0]
    total = sum(counts.values())
    need = total // 2 + 1 if strict else total
    if n < need: raise ValueError(f"no quorum: {n}/{total}")
    return win, n

@dataclass
class Epoch:
    current: int = 0
    history: List[int] = field(default_factory=list)
    def bump(self) -> int:
        self.current += 1; self.history.append(self.current); return self.current

def reconcile(replicas):
    out = {}
    for r in replicas:
        for k, v in r.items():
            if k not in out or v > out[k]: out[k] = v
    return out

def coordinate() -> str:
    return "coordinate: quorum + epoch + reconcile ready"
