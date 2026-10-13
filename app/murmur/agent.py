"""Agent — one bird. Ticks at high frequency. No planning.

Rule engine output overrides the stage decision when present.
Both go through `apply`, so state is updated consistently.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.murmur.rules import Rule, select
from app.murmur.state import AgentState, Decision, Update


@dataclass
class Agent:
    state: AgentState
    rules: list[Rule] = field(default_factory=list)
    neighbors: list[Agent] = field(default_factory=list)

    def decide(self) -> Decision | None:
        self.state.ticks += 1
        self.state.last_tick_ts = time.time()
        return select(self.state, [n.state for n in self.neighbors],
                      self.rules)

    def apply(self, d: Decision, dt: float = 0.1) -> None:
        v = d.verb
        p = d.params or {}
        if v == "act.recenter":
            g = float(p.get("gain", 0.2))
            for k in list(self.state.position):
                b = self.state.baseline.get(k, self.state.position[k])
                cur = self.state.position[k]
                self.state.position[k] = cur + (b - cur) * g
        elif v == "act.dampen":
            f = float(p.get("factor", 0.5))
            for k in list(self.state.velocity):
                self.state.velocity[k] *= f
        elif v == "act.align":
            k = str(p.get("key", "signal"))
            t = float(p.get("target", 0.0))
            cur = self.state.position.get(k, 0.0)
            self.state.position[k] = cur + (t - cur) * 0.5
        elif v == "act.probe":
            amp = float(p.get("amplitude", 0.02))
            self.state.position["signal"] = (
                self.state.position.get("signal", 0.0) + amp)
        self._advance(dt)

    def _advance(self, dt: float) -> None:
        for k in list(self.state.position):
            v = self.state.velocity.get(k, 0.0)
            self.state.position[k] = self.state.position.get(k, 0.0) + v * dt
        # Fold signal phase into a double-double reference
        # so a long run does not drift. DDChain attached
        # lazily on first _advance call.
        try:
            if not hasattr(self, "_dd"):
                from app.ddlong.chain import DDChain
                self._dd = DDChain(node_id=self.id)
            sig = self.state.position.get("signal")
            if sig is not None:
                self._dd.observe_phase(float(sig))
        except Exception:
            pass

    def apply_update(self, u: Update) -> None:
        if u.threshold:
            for k in list(self.state.thresholds):
                self.state.thresholds[k] = max(
                    0.05, self.state.thresholds[k] + u.threshold)
