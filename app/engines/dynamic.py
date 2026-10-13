"""Dynamic difficulty controller.

Per kind:
    if mean_rate > high_threshold:  raise difficulty
    if mean_rate < low_threshold:   lower difficulty

The thresholds and step are configurable. The controller keeps
a history so you can see the difficulty trajectory.
"""
from __future__ import annotations

from dataclasses import dataclass, field

LEVELS = ("easy", "medium", "hard")


@dataclass
class DifficultyState:
    kind: str
    level: str = "medium"

    def _idx(self) -> int:
        return LEVELS.index(self.level)

    def raise_(self) -> None:
        i = self._idx()
        if i < len(LEVELS) - 1:
            self.level = LEVELS[i + 1]

    def lower(self) -> None:
        i = self._idx()
        if i > 0:
            self.level = LEVELS[i - 1]


@dataclass
class Controller:
    high: float = 0.85
    low: float = 0.25
    state: dict[str, DifficultyState] = field(default_factory=dict)
    _interval: dict[str, list] = field(default_factory=dict)
    history: list[dict[str, str]] = field(default_factory=list)

    def initialise(self, kinds) -> None:
        for k in kinds:
            self.state[k] = DifficultyState(kind=k, level="medium")
        self.history.append({k: s.level for k, s in self.state.items()})

    def step(self, rate_by_kind: dict[str, float]) -> dict[str, str]:
        """Narrow the difficulty interval by φ per step.

        For each kind, we hold a continuous difficulty value d in
        [0, 2] mapped to LEVELS[0..2]. If the rate is inside
        [low, high], we do nothing. If it is above high, we shrink
        the upper bound toward the current level by PHI_INV. If
        below low, we shrink the lower bound upward by PHI_INV.
        The interval [lo, hi] starts at [0, 2] and converges to
        the difficulty that lands the rate inside [low, high].
        """
        from app.sacred.constants import PHI_INV
        for k, r in rate_by_kind.items():
            s = self.state.get(k)
            if s is None:
                continue
            interval = self._interval.setdefault(k, [0.0, 2.0])
            # map current level to a numeric coordinate
            cur = float(LEVELS.index(s.level))
            if r >= self.high:
                # too easy: raise, and tighten the lower bound to cur
                interval[0] = max(interval[0], cur)
                s.raise_()
            elif r <= self.low:
                # too hard: lower, and tighten the upper bound to cur
                interval[1] = min(interval[1], cur)
                s.lower()
            else:
                # inside band: narrow the interval by φ around cur
                width = interval[1] - interval[0]
                interval[0] = cur - width * PHI_INV / 2.0
                interval[1] = cur + width * PHI_INV / 2.0
        snap = {k: s.level for k, s in self.state.items()}
        self.history.append(snap)
        return snap

    def current(self) -> dict[str, str]:
        return {k: s.level for k, s in self.state.items()}

    def to_dict(self) -> dict:
        return {"current": self.current(), "history": self.history}
