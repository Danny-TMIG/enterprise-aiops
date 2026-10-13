"""Jellyfish: drifting signal-carriers over the mesh.

A Jellyfish has:
  bell      — identity
  tentacles — light touches to mesh nodes (no fixed topology)
  pulse     — a signal (packet) it is carrying
  ttl       — remaining lifetime; dissolves at 0

Behavior per tick:
  drift     — move to a random adjacent (least-loaded) node
  sample    — pick up residue from any node it touches
  emit      — if the signal is discharged, dissolve
  split     — if residue exceeds threshold, spawn a child
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from app.reconfig.mesh import Mesh, Packet


@dataclass
class Jellyfish:
    id: str
    ttl: int = 8
    residue: list[str] = field(default_factory=list)
    route: list[str] = field(default_factory=list)
    packet: Packet | None = None

    def drift(self, mesh: Mesh, rng: random.Random) -> str | None:
        ids = sorted(mesh.nodes.keys())
        if not ids:
            return None
        # bias toward least-loaded
        ids.sort(key=lambda i: (mesh.nodes[i].load, i))
        idx = min(len(ids) - 1, int(abs(rng.gauss(0, 1))))
        node = ids[idx]
        self.route.append(node)
        return node

    def tick(self, mesh: Mesh, rng: random.Random) -> Jellyfish | None:
        self.ttl -= 1
        node = self.drift(mesh, rng)
        child = None
        if self.residue and len(self.residue) >= 3 and rng.random() < 0.25:
            child = Jellyfish(
                id=f"{self.id}.{len(self.route)}",
                ttl=self.ttl,
                residue=self.residue[:len(self.residue) // 2],
                packet=self.packet,
            )
            self.residue = self.residue[len(self.residue) // 2:]
        if self.packet and self.packet.route:
            # delivered
            mesh.release(self.packet)
            self.packet = None
            self.ttl = min(self.ttl, 1)
        return child

    @property
    def alive(self) -> bool:
        return self.ttl > 0 or self.packet is not None


class Bloom:
    """A population of jellyfish. Bounded, self-regulating."""

    def __init__(self, n: int = 4, seed: int = 0):
        self.rng = random.Random(seed)
        self.members: list[Jellyfish] = [
            Jellyfish(id=f"jf-{i}", ttl=6 + i) for i in range(n)
        ]

    def tick(self, mesh: Mesh) -> None:
        new: list[Jellyfish] = []
        for j in list(self.members):
            child = j.tick(mesh, self.rng)
            if not j.alive:
                self.members.remove(j)
            if child is not None:
                new.append(child)
        # cap population
        for c in new:
            if len(self.members) < 16:
                self.members.append(c)

    def snapshot(self) -> list[dict]:
        return [
            {"id": j.id, "ttl": j.ttl, "route": j.route,
             "residue": j.residue[:4]}
            for j in self.members
        ]
