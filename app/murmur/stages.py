"""The nine stages. Every tick runs them in order, per agent."""
from __future__ import annotations

import importlib
from typing import Any

from app.murmur.connectors import call as tool_call
from app.murmur.state import (
    AgentState,
    Allocation,
    Coordination,
    Decision,
    Effect,
    Forecast,
    Signal,
    Situation,
    Update,
    Verdict,
)


def _swarm():
    try:
        return importlib.import_module("app.origami.swarm")
    except Exception:
        return None


def sense(state: AgentState, ctx: dict[str, Any]) -> Signal:
    src = ctx.get("source", "local")
    kind = ctx.get("kind", "drift")
    base = state.baseline.get("signal", 0.0)
    cur = state.position.get("signal", 0.0)
    value = abs(cur - base)
    return Signal(source=src, kind=kind, value=value,
                  payload={"baseline": base, "current": cur})


def interpret(sig: Signal, state: AgentState) -> Situation:
    dev = sig.value / max(0.001, state.thresholds.get("drift", 0.5))
    label = "nominal"
    if dev > 2.0:
        label = "acute"
    elif dev > 1.0:
        label = "elevated"
    return Situation(label=label,
                     confidence=min(1.0, dev / 2.0),
                     deviation=dev,
                     features={"sig": sig.value})


def predict(sit: Situation, state: AgentState) -> Forecast:
    risk = min(1.0, sit.deviation * 0.5)
    if sit.label == "acute":
        return Forecast("escalate", 0.8, risk, 1.0)
    if sit.label == "elevated":
        return Forecast("adjust", 0.6, risk, 2.0)
    return Forecast("hold", 0.9, risk, 5.0)


def decide(fc: Forecast, sit: Situation, state: AgentState) -> Decision:
    if fc.outcome == "escalate":
        return Decision("act.recenter", {"gain": 0.35}, urgency=0.9)
    if fc.outcome == "adjust":
        return Decision("act.align", {"key": "signal",
                                       "target": state.baseline.get("signal", 0.0)},
                        urgency=0.5)
    return Decision("act.probe", {"amplitude": 0.02}, urgency=0.1)


def act(d: Decision, state: AgentState,
        tool: str | None = None) -> Effect:
    if tool:
        res = tool_call(tool, "act",
                        {"summary": d.verb, "params": d.params})
        return Effect(verb=d.verb, ok=bool(res.get("ok")),
                      detail=str(res.get("detail", "")), tool=tool)
    return Effect(verb=d.verb, ok=True, detail="local")


def coordinate(state: AgentState, peers: list[AgentState]) -> Coordination:
    overlap = 0
    for p in peers:
        if abs(p.position.get("signal", 0.0)
               - state.position.get("signal", 0.0)) < 0.05:
            overlap += 1
    return Coordination(
        peers=[p.agent_id for p in peers],
        overlaps=overlap,
        delegates=[],
    )


def allocate(co: Coordination, state: AgentState,
             budget: float = 1.0) -> Allocation:
    # more peers agreeing, the less each spends
    share = 1.0 / (1.0 + co.overlaps)
    cap = budget * share
    hit = cap < 0.05
    return Allocation(share=round(share, 3),
                      budget=round(cap, 3), cap_hit=hit)


def verify(e: Effect, fc: Forecast) -> Verdict:
    ok = e.ok and fc.risk < 0.9
    return Verdict(ok=ok, delta=fc.risk - (0.0 if e.ok else 1.0),
                   reason="ok" if ok else "effect_or_risk")


def learn(v: Verdict, state: AgentState) -> Update:
    if v.ok:
        return Update(threshold=-0.005, weight=0.005, reason="reinforce")
    return Update(threshold=+0.02, weight=-0.02, reason="chastise")
