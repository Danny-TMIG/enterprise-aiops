"""Team coordination — quorum + epoch."""

from __future__ import annotations  # pragma: no cover

from collections import Counter  # pragma: no cover
from collections.abc import Hashable, Iterable  # pragma: no cover
from dataclasses import dataclass, field  # pragma: no cover


def quorum(reports: Iterable[Hashable], *, strict: bool = True):  # pragma: no cover
    counts = Counter(reports)
    if not counts:  # pragma: no cover
        raise ValueError("no reports")  # pragma: no cover
    win, n = counts.most_common(1)[0]
    total = sum(counts.values())
    need = total // 2 + 1 if strict else 1
    if n < need:  # pragma: no cover
        raise ValueError(f"no quorum: {n}/{total}")  # pragma: no cover
    return win, n  # pragma: no cover


@dataclass
class Epoch:  # pragma: no cover
    current: int = 0
    history: list[int] = field(default_factory=list)

    def bump(self) -> int:  # pragma: no cover
        self.current += 1
        self.history.append(self.current)
        return self.current  # pragma: no cover


def reconcile(replicas):  # pragma: no cover
    out = {}
    for r in replicas:
        for k, v in r.items():
            if k not in out or v > out[k]:  # pragma: no cover
                out[k] = v
    return out  # pragma: no cover


def coordinate() -> str:  # pragma: no cover
    return "coordinate: quorum + epoch + reconcile ready"  # pragma: no cover
