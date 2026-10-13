"""Difference engine.

Three levels of difference, in the sense of Newton's forward
differences over a sequence of generations:

    Level 0  raw outcomes
    Level 1  per-solver success rate r[s][g]
    Level 2  pairwise delta     D[s1,s2][g] = r[s1][g] - r[s2][g]
    Level 3  delta-of-delta     DD[s1,s2][g] = D[s1,s2][g] - D[s1,s2][g-1]

Level 3 is the one that answers "is s1 gaining on s2".
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DiffLevels:
    kind: str
    solvers: list[str]
    # rate[g][solver] = success rate at generation g
    rate: list[dict[str, float]] = field(default_factory=list)
    # delta[g][(s1, s2)] = rate[s1] - rate[s2]  (positive => s1 > s2)
    delta: list[dict[tuple[str, str], float]] = field(default_factory=list)
    # ddelta[g][(s1, s2)] = delta[g] - delta[g-1]
    ddelta: list[dict[tuple[str, str], float]] = field(default_factory=list)

    def push(self, rate: dict[str, float]) -> None:
        self.rate.append(rate)
        solvers = self.solvers
        d: dict[tuple[str, str], float] = {}
        for s1 in solvers:
            for s2 in solvers:
                if s1 == s2:
                    continue
                d[(s1, s2)] = rate.get(s1, 0.0) - rate.get(s2, 0.0)
        self.delta.append(d)
        if len(self.delta) == 1:
            self.ddelta.append({k: 0.0 for k in d})
        else:
            prev = self.delta[-2]
            self.ddelta.append({k: d[k] - prev.get(k, 0.0) for k in d})

    def latest_delta(self) -> dict[tuple[str, str], float]:
        return self.delta[-1] if self.delta else {}

    def latest_ddelta(self) -> dict[tuple[str, str], float]:
        return self.ddelta[-1] if self.ddelta else {}

    def dominant(self) -> str | None:
        """Solver with highest mean rate over all generations."""
        if not self.rate:
            return None
        acc: dict[str, list[float]] = {s: [] for s in self.solvers}
        for r in self.rate:
            for s in self.solvers:
                acc[s].append(r.get(s, 0.0))
        return max(acc, key=lambda s: sum(acc[s]) / max(len(acc[s]), 1))

    def improving(self) -> list[tuple[str, float]]:
        """(solver, sum of positive ddelta) sorted descending."""
        if not self.ddelta:
            return []
        acc: dict[str, float] = {s: 0.0 for s in self.solvers}
        for dd in self.ddelta:
            for (s1, s2), v in dd.items():
                if v > 0:
                    acc[s1] += v
        return sorted(acc.items(), key=lambda kv: -kv[1])


class DiffEngine:
    """One DiffLevels per kind."""

    def __init__(self, solvers_by_kind: dict[str, list[str]]):
        self.by_kind: dict[str, DiffLevels] = {
            k: DiffLevels(kind=k, solvers=list(v))
            for k, v in solvers_by_kind.items()
        }

    def push(self, kind: str, rate: dict[str, float]) -> None:
        self.by_kind[kind].push(rate)

    def summary(self) -> dict:
        out = {}
        for k, d in self.by_kind.items():
            out[k] = {
                "generations": len(d.rate),
                "dominant": d.dominant(),
                "improving": d.improving()[:3],
                "latest_delta": {f"{a}|{b}": round(v, 4)
                                 for (a, b), v in d.latest_delta().items()},
            }
        return out
