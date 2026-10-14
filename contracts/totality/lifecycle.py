"""Totality of the canonical lifecycle.

The Governed Lifecycle has twelve stages. Every consequential action
passes through every stage in order, or fails at the stage where the
boundary rejects it. No stage can be skipped.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    n: int
    name: str
    owner: str


GOVERNED_STAGES: tuple[Stage, ...] = (
    Stage(1, "receive", "Govern"),
    Stage(2, "resolve identity", "Govern"),
    Stage(3, "resolve authority", "Govern"),
    Stage(4, "classify information", "Govern"),
    Stage(5, "evaluate policy", "Govern"),
    Stage(6, "control information flow", "Govern"),
    Stage(7, "resolve capability", "Govern"),
    Stage(8, "obtain human decision", "Govern"),
    Stage(9, "issue execution order", "Govern"),
    Stage(10, "monitor changes", "Govern"),
    Stage(11, "verify return", "Govern"),
    Stage(12, "close and re-enter", "Govern"),
)


COGNITIVE_STAGES: tuple[Stage, ...] = (
    Stage(1, "receive", "Cognition"),
    Stage(2, "represent", "Cognition"),
    Stage(3, "resolve state", "Cognition"),
    Stage(4, "ground", "Cognition"),
    Stage(5, "route", "Cognition"),
    Stage(6, "reason", "Cognition"),
    Stage(7, "plan", "Cognition"),
    Stage(8, "evaluate", "Cognition"),
    Stage(9, "respond", "Cognition"),
    Stage(10, "request action", "Cognition"),
    Stage(11, "realize", "Govern + Compute"),
    Stage(12, "evidence and update", "Cognition"),
)


EXECUTION_STEPS: tuple[Stage, ...] = (
    Stage(1, "order receipt", "Compute"),
    Stage(2, "contract normalization", "Compute"),
    Stage(3, "workflow creation", "Compute"),
    Stage(4, "hardware and workload qualification", "Compute"),
    Stage(5, "topology resolution", "Compute"),
    Stage(6, "resource resolution", "Compute"),
    Stage(7, "admission and reservation", "Compute"),
    Stage(8, "execution planning", "Compute"),
    Stage(9, "scheduling and dispatch", "Compute"),
    Stage(10, "secure realization", "Compute"),
    Stage(11, "observation and control", "Compute"),
    Stage(12, "recovery", "Compute"),
    Stage(13, "output and cleanup", "Compute"),
    Stage(14, "evidence return", "Compute"),
)


def every_stage_has_owner(stages: tuple[Stage, ...]) -> bool:
    return all(bool(s.owner) for s in stages)


def stages_are_contiguous(stages: tuple[Stage, ...]) -> bool:
    return [s.n for s in stages] == list(range(1, len(stages) + 1))
