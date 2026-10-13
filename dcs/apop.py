"""Apoptosispoiesis — form by programmed death."""
from __future__ import annotations  # pragma: no cover

import random  # pragma: no cover
from dataclasses import dataclass, field  # pragma: no cover

from dcs.triad.lattice import CONFLICT, FAIL, PASS, UNKNOWN, VState  # pragma: no cover


@dataclass
class State:  # pragma: no cover
    id: str
    payload: dict = field(default_factory=dict)
    born: int = 0
    deaths: int = 0
    status: str = "alive"


@dataclass
class Death:  # pragma: no cover
    tick: int
    state_id: str
    verdict: VState
    kind: str
    evidence: dict = field(default_factory=dict)


@dataclass
class Population:  # pragma: no cover
    states: list[State] = field(default_factory=list)
    log: list[Death] = field(default_factory=list)
    tick: int = 0

    def add(self, s: State):  # pragma: no cover
        s.born = self.tick
        self.states.append(s)

    def alive(self):  # pragma: no cover
        return [s for s in self.states if s.status == "alive"]  # pragma: no cover

    def deferred(self):  # pragma: no cover
        return [s for s in self.states if s.status == "deferred"]  # pragma: no cover

    def conflicted(self):  # pragma: no cover
        return [s for s in self.states if s.status == "conflict"]  # pragma: no cover

    def step(self, sigma, *, necrotic_ratio: float = 0.0, rng=None):  # pragma: no cover
        rng = rng or random.Random()
        self.tick += 1
        for s in self.alive():
            v = sigma(s)
            if v == PASS:  # pragma: no cover
                s.status = "alive"
            elif v == FAIL:
                necrotic = rng.random() < necrotic_ratio
                s.status = "necrotic" if necrotic else "apoptotic"
                s.deaths += 1
                self.log.append(Death(
                    tick=self.tick, state_id=s.id, verdict=v, kind=s.status,
                    evidence={"payload_keys": sorted(s.payload.keys()),
                              "born": s.born, "lifetime": self.tick - s.born},
                ))
            elif v == UNKNOWN:
                s.status = "deferred"
            elif v == CONFLICT:
                s.status = "conflict"
        return self  # pragma: no cover

    def run(self, sigma, *, max_ticks=100, necrotic_ratio=0.0, seed=0):  # pragma: no cover
        rng = random.Random(seed)
        for _ in range(max_ticks):
            before = tuple(sorted(s.id for s in self.alive()))
            self.step(sigma, necrotic_ratio=necrotic_ratio, rng=rng)
            after = tuple(sorted(s.id for s in self.alive()))
            if before == after:  # pragma: no cover
                break
        return self  # pragma: no cover

    def form(self):  # pragma: no cover
        return sorted(self.alive(), key=lambda s: (s.born, s.id))  # pragma: no cover

    def stats(self):  # pragma: no cover
        return {  # pragma: no cover
            "tick": self.tick,
            "alive": len(self.alive()),
            "apoptotic": sum(1 for d in self.log if d.kind == "apoptotic"),
            "necrotic": sum(1 for d in self.log if d.kind == "necrotic"),
            "deferred": len(self.deferred()),
            "conflicted": len(self.conflicted()),
            "survival_rate": len(self.alive()) / max(1, len(self.states)),
        }


def sigma_from_triad(kernel, spec_for):  # pragma: no cover
    def sigma(s: State) -> VState:  # pragma: no cover
        t = kernel.verify(spec_for(s))
        return {"PASS": PASS, "FAIL": FAIL,  # pragma: no cover
                "UNKNOWN": UNKNOWN, "CONFLICT": CONFLICT}[t.verdict()]
    return sigma  # pragma: no cover
