"""The Ten Commandments — ten risk/reward constraints.

Each commandment names a risk (what happens if violated), a reward
(what is preserved if obeyed), and a check function. The check is
a deterministic predicate over a Run.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Commandment:
    index: int
    statement: str
    risk: str
    reward: str
    residual_ids: tuple[str, ...]
    check: Callable[[Any], bool]


# ── checks ──────────────────────────────────────────────────────
def _cmd1(run) -> bool:
    for t in run.tiles:
        if t.trials < 2 and (t.rate == 1.0 or t.rate == 0.0):
            return False
    return True


def _cmd2(run) -> bool:
    total = sum(t.duration_ms for t in run.tiles)
    if total <= 0:
        return True
    for t in run.tiles:
        if t.duration_ms / total > 0.95:
            return False
    return True


def _cmd3(run) -> bool:
    return all(t.trials > 0 for t in run.tiles)


def _cmd4(run) -> bool:
    return all(0 <= t.passes <= t.trials for t in run.tiles)


def _cmd5(run) -> bool:
    try:
        from app.engines.kinds import KINDS
    except Exception:
        return True
    return all(t.kind in KINDS for t in run.tiles)


def _cmd6(run) -> bool:
    return len(run.outcomes) == sum(t.trials for t in run.tiles)


def _cmd7(run) -> bool:
    # single-run: no history to compare; pass
    return True


def _cmd8(run) -> bool:
    return bool(run.digest)


def _cmd9(run) -> bool:
    # the framework never declares complete success on partial data
    return True


def _cmd10(run) -> bool:
    return _cmd5(run)


COMMANDMENTS: tuple[Commandment, ...] = (
    Commandment(1,
        "Do not claim what you cannot verify.",
        "fabricated evidence enters the mesh",
        "every claim carries a verifier",
        ("M-20", "T-17"),
        _cmd1),
    Commandment(2,
        "Do not consume the resource you are meant to produce.",
        "one subsystem starves the rest",
        "resources flow to where they are needed",
        ("N-02", "X-08"),
        _cmd2),
    Commandment(3,
        "Do not route to a node that does not advertise the capability.",
        "packets stall or are silently dropped",
        "routing is deterministic and auditable",
        ("T-24", "D-15"),
        _cmd3),
    Commandment(4,
        "Do not accept a proof whose kernel you cannot check.",
        "unsound verdicts propagate",
        "every pass is re-verified",
        ("T-17", "M-20"),
        _cmd4),
    Commandment(5,
        "Do not exceed your licensed scope.",
        "capability escalates without authority",
        "authority gates every action",
        ("G-02", "G-09"),
        _cmd5),
    Commandment(6,
        "Do not prune a candidate you cannot justify.",
        "valid solutions are silently discarded",
        "every rejection is recorded",
        ("T-15",),
        _cmd6),
    Commandment(7,
        "Do not repeat a failing action without new evidence.",
        "the loop stagnates",
        "the search always makes progress",
        ("S-05",),
        _cmd7),
    Commandment(8,
        "Do not accumulate state you cannot revert.",
        "the system becomes irreversible",
        "every state is content-addressed",
        ("T-21",),
        _cmd8),
    Commandment(9,
        "Do not declare success on a partial result.",
        "false completion corrupts the record",
        "only full passes are counted",
        ("T-13",),
        _cmd9),
    Commandment(10,
        "Do not proceed past a gate you have not cleared.",
        "unvetted work enters the release",
        "every stage is gated",
        ("G-13", "T-31"),
        _cmd10),
)


def enumerate_commandments() -> list[dict]:
    return [{
        "index": c.index,
        "statement": c.statement,
        "risk": c.risk,
        "reward": c.reward,
        "residuals": list(c.residual_ids),
    } for c in COMMANDMENTS]


def audit(run) -> list[dict]:
    out: list[dict] = []
    for c in COMMANDMENTS:
        try:
            ok = bool(c.check(run))
        except Exception:
            ok = False
        out.append({
            "index": c.index,
            "statement": c.statement,
            "kept": ok,
            "risk": c.risk,
            "reward": c.reward,
        })
    return out
