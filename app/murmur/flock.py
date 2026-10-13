"""Flock — N agents, one shared clock, one local tick per bird."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.murmur import stages
from app.murmur.agent import Agent
from app.murmur.rules import default_rules
from app.murmur.state import AgentState


@dataclass
class Flock:
    n: int = 8
    history_path: str = ".murmur/history.jsonl"
    agents: list[Agent] = field(default_factory=list)
    tick_count: int = 0
    last_metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        import random
        self.agents = []
        rules = default_rules()
        for i in range(self.n):
            s = AgentState(
                agent_id=f"a{i}",
                position={"signal": random.uniform(-0.2, 0.2)},
                velocity={"signal": 0.0},
                baseline={"signal": 0.0},
                thresholds={"drift": 0.4, "speed": 2.0, "outlier": 0.8},
                weights={"drift": 1.0},
            )
            self.agents.append(Agent(state=s, rules=list(rules)))

    def neighbors_of(self, idx: int, radius: int = 2) -> list[Agent]:
        out = []
        for j in range(max(0, idx - radius),
                       min(self.n, idx + radius + 1)):
            if j != idx:
                out.append(self.agents[j])
        return out

    def tick(self, dt: float = 0.05, tool: str | None = None) -> dict[str, Any]:
        self.tick_count += 1

        # update neighbor lists (small rule, high frequency)
        for i, a in enumerate(self.agents):
            a.neighbors = self.neighbors_of(i)

        effects: list[dict[str, Any]] = []
        for a in self.agents:
            sig = stages.sense(a.state, {"kind": "drift"})
            sit = stages.interpret(sig, a.state)
            fc = stages.predict(sit, a.state)
            stage_d = stages.decide(fc, sit, a.state)

            # rule engine wins if it produces a decision
            rd = a.decide()
            d = rd if rd is not None else stage_d
            a.apply(d, dt)

            e = stages.act(d, a.state, tool=tool)
            co = stages.coordinate(a.state,
                                   [n.state for n in a.neighbors])
            al = stages.allocate(co, a.state)
            v = stages.verify(e, fc)
            u = stages.learn(v, a.state)

            a.apply_update(u)
            a.state.last_effect = e
            a.state.last_verdict = v

            effects.append({
                "agent": a.state.agent_id,
                "situation": sit.label,
                "forecast": fc.outcome,
                "decision": d.verb,
                "effect": e.ok,
                "alloc_share": al.share,
                "verdict": v.ok,
                "update": u.reason,
            })

        self._record(effects)
        self._metrics(effects)
        return {"tick": self.tick_count, "effects": effects,
                "metrics": self.last_metrics}

    def _record(self, effects: list[dict[str, Any]]) -> None:
        p = Path(self.history_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        rec = {"tick": self.tick_count, "ts": time.time(),
               "effects": effects}
        with p.open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def _metrics(self, effects: list[dict[str, Any]]) -> None:
        n = max(1, len(effects))
        ok = sum(1 for e in effects if e["effect"])
        aligned = sum(1 for e in effects if e["decision"] == "act.align")
        recentered = sum(1 for e in effects
                         if e["decision"] == "act.recenter")
        self.last_metrics = {
            "effect_ok_rate": round(ok / n, 3),
            "aligned_rate": round(aligned / n, 3),
            "recentered_rate": round(recentered / n, 3),
            "mean_deviation": round(
                sum(abs(a.state.position.get("signal", 0.0)
                        - a.state.baseline.get("signal", 0.0))
                    for a in self.agents) / n, 4),
        }

    def run(self, ticks: int = 50, dt: float = 0.05,
            tool: str | None = None,
            on_tick: Any | None = None) -> list[dict[str, Any]]:
        out = []
        for _ in range(ticks):
            r = self.tick(dt=dt, tool=tool)
            out.append(r)
            if on_tick:
                on_tick(r)
        return out
