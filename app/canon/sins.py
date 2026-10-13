"""The Seven Sins — seven ways a subsystem fails.

Each sin is a detection function over a `Run`. Each detection is
grounded in residual IDs from the register.

    Pride     claims competence not earned
    Greed     consumes more than it produces
    Lust      drifts toward an unverifiable target
    Envy      succeeds by another's failure
    Gluttony  exhausts a shared resource
    Wrath     destroys the invariant it preserves
    Sloth     refuses to attempt
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SinSpec:
    index: int
    name: str
    description: str
    detection: str
    residual_ids: tuple[str, ...]
    remedy: str


@dataclass
class SinRecord:
    sin: str
    subject: str
    evidence: str
    residuals: list[str]
    remedy: str

    def to_dict(self):
        return {"sin": self.sin, "subject": self.subject,
                "evidence": self.evidence,
                "residuals": list(self.residuals),
                "remedy": self.remedy}


SIN_SPECS: tuple[SinSpec, ...] = (
    SinSpec(1, "Pride",
            "The solver claims competence it has not earned.",
            "rate == 1.0 on too few trials, or rate == 0.0 on too few",
            ("M-20", "T-13", "S-02"),
            "require a minimum number of trials per tile"),
    SinSpec(2, "Greed",
            "The solver consumes more resources than it produces.",
            "duration_ms / passes exceeds a cost threshold",
            ("N-02", "N-16", "N-17"),
            "cap duration or downgrade to a cheaper solver"),
    SinSpec(3, "Lust",
            "The solver drifts toward an unverifiable target.",
            "rate == 0.0 on many trials",
            ("M-04", "T-16", "M-23"),
            "cap the iteration count and record the residue"),
    SinSpec(4, "Envy",
            "Success depends on another solver's failure.",
            "max(rate) == 1.0 and min(rate) == 0.0 on the same kind",
            ("D-15", "M-21", "N-06"),
            "route by capability, not by scarcity"),
    SinSpec(5, "Gluttony",
            "The solver exhausts a shared resource.",
            "one tile consumes > 90% of the run duration",
            ("X-08", "T-26", "P-14"),
            "enforce quotas at the substrate"),
    SinSpec(6, "Wrath",
            "The solver destroys the invariant it was meant to preserve.",
            "fails puzzles other solvers solve on the same kind",
            ("T-07", "T-17", "T-34"),
            "check the invariant on both sides of every step"),
    SinSpec(7, "Sloth",
            "The solver refuses to attempt.",
            "zero-duration failure on a non-trivial puzzle",
            ("C-19", "T-13", "E-16"),
            "escalate the difficulty or route to a stronger solver"),
)


# ── detectors ───────────────────────────────────────────────────
def detect_pride(run, min_trials: int = 4) -> list[SinRecord]:
    out: list[SinRecord] = []
    for t in run.tiles:
        if t.trials < min_trials and (t.rate == 1.0 or t.rate == 0.0):
            out.append(SinRecord(
                "Pride",
                f"{t.kind}/{t.solver}/{t.difficulty}",
                f"rate={t.rate:.2f} on {t.trials} trials",
                ["M-20", "T-13", "S-02"],
                "raise puzzles_per_tile above the minimum"))
    return out


def detect_greed(run, cost_threshold_ms: float = 2000.0
                 ) -> list[SinRecord]:
    out: list[SinRecord] = []
    for t in run.tiles:
        if t.passes == 0:
            continue
        cpp = t.duration_ms / max(t.passes, 1)
        if cpp > cost_threshold_ms:
            out.append(SinRecord(
                "Greed",
                f"{t.kind}/{t.solver}/{t.difficulty}",
                f"cost_per_pass={cpp:.1f}ms > {cost_threshold_ms}",
                ["N-02", "N-16", "N-17"],
                "cap duration or downgrade to a cheaper solver"))
    return out


def detect_lust(run, min_trials: int = 4) -> list[SinRecord]:
    out: list[SinRecord] = []
    for t in run.tiles:
        if t.rate == 0.0 and t.trials >= min_trials:
            out.append(SinRecord(
                "Lust",
                f"{t.kind}/{t.solver}/{t.difficulty}",
                f"rate=0.0 on {t.trials} trials",
                ["M-04", "T-16", "M-23"],
                "cap iterations or route to a stronger solver"))
    return out


def detect_envy(run_a, run_b) -> list[SinRecord]:
    """Envy needs a pair. Same kind, one solver at 1.0, one at 0.0."""
    out: list[SinRecord] = []
    by_kind: dict[str, list[Any]] = {}
    for t in run_a.tiles:
        by_kind.setdefault(t.kind, []).append(t)
    for kind, tiles in by_kind.items():
        rates = [t.rate for t in tiles]
        if not rates:
            continue
        if max(rates) == 1.0 and min(rates) == 0.0:
            for t in tiles:
                if t.rate == 0.0:
                    out.append(SinRecord(
                        "Envy",
                        f"{kind}/{t.solver}/{t.difficulty}",
                        "rate=0.0 while peer solver is 1.0",
                        ["D-15", "M-21", "N-06"],
                        "route by capability, not by scarcity"))
    return out


def detect_gluttony(run, share_threshold: float = 0.90
                   ) -> list[SinRecord]:
    total = sum(t.duration_ms for t in run.tiles)
    if total <= 0:
        return []
    out: list[SinRecord] = []
    for t in run.tiles:
        if t.duration_ms / total > share_threshold:
            out.append(SinRecord(
                "Gluttony",
                f"{t.kind}/{t.solver}/{t.difficulty}",
                f"consumed {100 * t.duration_ms / total:.1f}% "
                f"of run duration",
                ["X-08", "T-26", "P-14"],
                "enforce quotas at the substrate"))
    return out


def detect_wrath(run) -> list[SinRecord]:
    out: list[SinRecord] = []
    by_puzzle: dict[tuple, list[Any]] = {}
    for o in run.outcomes:
        key = (o.kind, o.difficulty, o.puzzle_id)
        by_puzzle.setdefault(key, []).append(o)
    for key, outs in by_puzzle.items():
        flags = [o.passed for o in outs]
        if flags and any(flags) and not all(flags):
            for o in outs:
                if not o.passed:
                    out.append(SinRecord(
                        "Wrath",
                        f"{o.kind}/{o.solver}/"
                        f"{o.difficulty}#{o.puzzle_id}",
                        "failed a puzzle that peers solved",
                        ["T-07", "T-17", "T-34"],
                        "check invariants on both sides of every step"))
    return out


def detect_sloth(run) -> list[SinRecord]:
    out: list[SinRecord] = []
    for o in run.outcomes:
        if o.duration_ms == 0.0 and not o.passed:
            out.append(SinRecord(
                "Sloth",
                f"{o.kind}/{o.solver}/"
                f"{o.difficulty}#{o.puzzle_id}",
                "zero-duration failure",
                ["C-19", "T-13", "E-16"],
                "escalate difficulty or route to a stronger solver"))
    return out


DETECTORS = {
    "Pride":    detect_pride,
    "Greed":    detect_greed,
    "Lust":     detect_lust,
    "Gluttony": detect_gluttony,
    "Wrath":    detect_wrath,
    "Sloth":    detect_sloth,
    "Envy":     detect_envy,   # needs two runs
}


def enumerate_sins() -> list[dict]:
    return [{
        "index": s.index, "name": s.name,
        "description": s.description,
        "detection": s.detection,
        "residuals": list(s.residual_ids),
        "remedy": s.remedy,
    } for s in SIN_SPECS]


def detect_all(runs: list[Any]) -> list[SinRecord]:
    out: list[SinRecord] = []
    single = ["Pride", "Greed", "Lust", "Gluttony", "Wrath", "Sloth"]
    for run in runs:
        for name in single:
            out.extend(DETECTORS[name](run))
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            out.extend(detect_envy(runs[i], runs[j]))
    return out
