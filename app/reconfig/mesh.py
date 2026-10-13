"""The mesh: capability-advertising nodes and content-addressed packets."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.reconfig.codeal import CAProgram


@dataclass
class Node:
    id: str
    capabilities: list[str]
    load: int = 0


@dataclass
class Packet:
    id: str
    program: CAProgram
    origin: str
    route: list[str] = field(default_factory=list)


class Mesh:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.inflight: list[Packet] = []

    def register(self, node: Node) -> None:
        self.nodes[node.id] = node

    def route(self, p: Packet) -> Node | None:
        """Deterministic: pick the least-loaded node that advertises
        every op present in the program."""
        ops = {i.op for i in p.program.instructions}
        candidates = [
            n for n in self.nodes.values()
            if ops.issubset(set(n.capabilities))
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda n: (n.load, n.id))
        chosen = candidates[0]
        chosen.load += 1
        p.route.append(chosen.id)
        self.inflight.append(p)
        return chosen

    def release(self, p: Packet) -> None:
        if p in self.inflight:
            self.inflight.remove(p)
        for nid in p.route:
            n = self.nodes.get(nid)
            if n:
                n.load = max(0, n.load - 1)
