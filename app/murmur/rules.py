"""Local rules — the entire intelligence of a murmuration.

Every rule sees only: (own state, neighbor states). It returns
None or a Decision. No rule can see the whole flock, no rule
plans more than one tick ahead.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.murmur.state import AgentState, Decision


@dataclass
class Rule:
    name: str
    when: Callable[[AgentState, list[AgentState]], bool]
    act: Callable[[AgentState, list[AgentState]], Decision]
    priority: int = 100
    weight: float = 1.0


def _avg_neighbor(state: AgentState, neighbors: list[AgentState],
                  key: str, default: float = 0.0) -> float:
    if not neighbors:
        return default
    total = 0.0
    for n in neighbors:
        total += n.position.get(key, default)
    return total / len(neighbors)


# ── the default flock rule set ─────────────────────────────────
def default_rules() -> list[Rule]:
    rules: list[Rule] = []

    def drift_when(s, ns):
        return s.deviation() > s.thresholds.get("drift", 0.5)

    def drift_act(s, ns):
        return Decision(verb="act.recenter", params={"gain": 0.2},
                        urgency=min(1.0, s.deviation()))

    rules.append(Rule("drift", drift_when, drift_act, priority=10))

    def too_fast_when(s, ns):
        speed = sum(abs(v) for v in s.velocity.values())
        return speed > s.thresholds.get("speed", 2.0)

    def too_fast_act(s, ns):
        return Decision(verb="act.dampen", params={"factor": 0.5},
                        urgency=0.4)

    rules.append(Rule("too_fast", too_fast_when, too_fast_act, priority=20))

    def outlier_when(s, ns):
        if not ns:
            return False
        k = "signal"
        v = s.position.get(k, 0.0)
        avg = _avg_neighbor(s, ns, k, v)
        return abs(v - avg) > s.thresholds.get("outlier", 1.0)

    def outlier_act(s, ns):
        k = "signal"
        avg = _avg_neighbor(s, ns, k, s.position.get(k, 0.0))
        return Decision(verb="act.align",
                        params={"key": k, "target": avg},
                        urgency=0.6)

    rules.append(Rule("outlier", outlier_when, outlier_act, priority=30))

    def lonely_when(s, ns):
        return len(ns) == 0

    def lonely_act(s, ns):
        return Decision(verb="coord.seek", params={"radius": 2.0},
                        urgency=0.2)

    rules.append(Rule("lonely", lonely_when, lonely_act, priority=50))

    def idle_when(s, ns):
        return s.last_effect is None

    def idle_act(s, ns):
        return Decision(verb="act.probe", params={"amplitude": 0.1},
                        urgency=0.05)

    rules.append(Rule("idle", idle_when, idle_act, priority=99))

    return rules


def select(state: AgentState, neighbors: list[AgentState],
           rules: list[Rule]) -> Decision | None:
    for r in sorted(rules, key=lambda x: x.priority):
        try:
            if r.when(state, neighbors):
                return r.act(state, neighbors)
        except Exception:
            continue
    return None
