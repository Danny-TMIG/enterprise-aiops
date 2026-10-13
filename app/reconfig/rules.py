"""Symbolic rewrite rules: IntentIR → partial TaskGraph."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.reconfig.intent_ir import IntentIR


@dataclass
class Task:
    id: str
    op: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    residue: list[str] = field(default_factory=list)


@dataclass
class Rule:
    name: str
    when: Callable[[IntentIR], bool]
    then: Callable[[IntentIR], list[Task]]


def _has_verb(ir: IntentIR, *verbs: str) -> bool:
    return any(v in ir.verbs for v in verbs)


def _rule_count_then_store(ir: IntentIR) -> list[Task]:
    return [
        Task(id="t1", op="COUNT",
             inputs=[ir.objects.get("input", "input")],
             outputs=["count"],
             residue=list(ir.residue)),
        Task(id="t2", op="STORE", inputs=["count"],
             outputs=["stored"],
             params={"target": ir.targets[0] if ir.targets else "memory"}),
    ]


def _rule_train_evaluate(ir: IntentIR) -> list[Task]:
    return [
        Task(id="t1", op="LOAD", inputs=["dataset"], outputs=["data"]),
        Task(id="t2", op="TRAIN", inputs=["data"], outputs=["model"],
             params={"target": ir.targets[0] if ir.targets else "mlx"}),
        Task(id="t3", op="EVALUATE", inputs=["model"],
             outputs=["metrics", "evidence"],
             params={"required": ir.evidence_required}),
        Task(id="t4", op="SCHEDULE", inputs=[],
             outputs=[],
             params={"every": _extract_cadence(ir)}),
    ]


def _rule_route_events(ir: IntentIR) -> list[Task]:
    return [
        Task(id="t1", op="FETCH", inputs=["source"], outputs=["events"]),
        Task(id="t2", op="FILTER", inputs=["events"], outputs=["matched"],
             params={"by": ir.objects.get("input", "key")}),
        Task(id="t3", op="ROUTE", inputs=["matched"], outputs=["routed"],
             params={"to": ir.targets[0] if ir.targets else "slack"}),
        Task(id="t4", op="RECORD", inputs=["routed"], outputs=["evidence"]),
    ]


def _extract_cadence(ir: IntentIR) -> str:
    for c in ir.constraints:
        if c.startswith("within:"):
            return c.split(":", 1)[1]
    return "daily"


RULES: list[Rule] = [
    Rule(
        name="count_then_store",
        when=lambda ir: _has_verb(ir, "COUNT") and _has_verb(ir, "STORE"),
        then=_rule_count_then_store,
    ),
    Rule(
        name="train_then_evaluate",
        when=lambda ir: _has_verb(ir, "TRAIN") and _has_verb(ir, "EVALUATE"),
        then=_rule_train_evaluate,
    ),
    Rule(
        name="route_events",
        when=lambda ir: _has_verb(ir, "ROUTE") and _has_verb(ir, "FETCH"),
        then=_rule_route_events,
    ),
    Rule(
        name="store_only",
        when=lambda ir: _has_verb(ir, "STORE") and not ir.verbs[:1],
        then=lambda ir: [Task(id="t1", op="STORE",
                              inputs=["input"], outputs=["stored"],
                              params={"target": ir.targets[0] if ir.targets else "memory"})],
    ),
]


def apply_rules(ir: IntentIR) -> tuple[list[Task], list[str]]:
    """Return (tasks, unmatched_names)."""
    tasks: list[Task] = []
    matched: list[str] = []
    for rule in RULES:
        try:
            if rule.when(ir):
                tasks.extend(rule.then(ir))
                matched.append(rule.name)
                break  # first matching rule wins
        except Exception:
            continue
    unmatched = [r.name for r in RULES if r.name not in matched]
    return tasks, unmatched
