"""Jellyfish over octet graphs.

A jellyfish drifts on the octet graph. Its pulse is an octet
fragment (a small OctetGraph). Its tentacles are the wires it
touches. It dissolves when the pulse matches a node it lands on
(matching value). It splits when the pulse contains a component
with > 2 nodes.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from app.octet.graph import OctetGraph
from app.octet.hyper import _components


@dataclass
class Jellyfish:
    id: str
    ttl: int = 8
    pulse: OctetGraph | None = None
    route: list[int] = field(default_factory=list)
    delivered: bool = False

    @property
    def alive(self) -> bool:
        return self.ttl > 0 and not self.delivered

    def tick(self, g: OctetGraph, rng: random.Random) -> Jellyfish | None:
        self.ttl -= 1
        ids = sorted(g.nodes.keys())
        if not ids:
            self.delivered = True
            return None
        nid = ids[int(abs(rng.gauss(0, 1))) % len(ids)]
        self.route.append(nid)
        node = g.nodes[nid]

        # delivery: if the pulse's largest value matches the node's value
        if self.pulse is not None and self.pulse.nodes:
            pv = max(o.value for o in self.pulse.nodes.values())
            if pv == node.value:
                self.delivered = True
                return None

        # split: if the pulse has > 2 nodes in any component
        child = None
        if self.pulse is not None:
            comps = _components(self.pulse)
            if comps and max(len(c.nodes) for c in comps) > 2 and rng.random() < 0.3:
                child = Jellyfish(
                    id=f"{self.id}.{len(self.route)}",
                    ttl=self.ttl,
                    pulse=None,
                    route=list(self.route),
                )
                # remove the largest component from the parent
                largest = max(comps, key=lambda c: len(c.nodes))
                self.pulse = largest
        return child


class Bloom:
    def __init__(self, n: int = 3, seed: int = 0):
        self.rng = random.Random(seed)
        self.members: list[Jellyfish] = [
            Jellyfish(id=f"jf-{i}", ttl=6 + i) for i in range(n)
        ]

    def seed_pulse(self, g: OctetGraph) -> None:
        for j in self.members:
            j.pulse = g.copy()

    def tick(self, g: OctetGraph) -> None:
        new = []
        for j in list(self.members):
            child = j.tick(g, self.rng)
            if not j.alive:
                self.members.remove(j)
            if child is not None and len(self.members) < 12:
                new.append(child)
        self.members.extend(new)

    def snapshot(self) -> list[dict]:
        return [{"id": j.id, "ttl": j.ttl,
                 "delivered": j.delivered,
                 "route_len": len(j.route)} for j in self.members]
