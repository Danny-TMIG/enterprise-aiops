from __future__ import annotations

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field

from app.octet.octet import PORTS, E, Octet

Port = tuple[int, int]


@dataclass
class OctetGraph:
    nodes: dict[int, Octet] = field(default_factory=dict)
    wires: dict[Port, Port] = field(default_factory=dict)
    _next_id: int = 0

    def new_node(self, kind: str, value: int = 0) -> int:
        nid = self._next_id
        self._next_id += 1
        self.nodes[nid] = Octet(kind, value)
        return nid

    def wire(self, p1: Port | None, p2: Port | None) -> None:
        if p1 is None or p2 is None:
            return
        self.wires[p1] = p2
        self.wires[p2] = p1

    def detach(self, p: Port) -> Port | None:
        other = self.wires.pop(p, None)
        if other is not None:
            self.wires.pop(other, None)
        return other

    def kill(self, nid: int) -> None:
        if nid not in self.nodes:
            return
        kind = self.nodes[nid].kind
        for idx in range(PORTS[kind]):
            self.detach((nid, idx))
        del self.nodes[nid]

    def active_pairs(self) -> Iterator[tuple[int, int]]:
        seen = set()
        for nid, oct_ in list(self.nodes.items()):
            if oct_.kind == E:
                # ε only interacts with anything wired to its principal
                pass
            other = self.wires.get((nid, 0))
            if other is None or other[1] != 0:
                continue
            onid = other[0]
            if onid not in self.nodes or onid <= nid:
                continue
            key = (nid, onid)
            if key in seen:
                continue
            seen.add(key)
            yield nid, onid

    def copy(self) -> OctetGraph:
        g = OctetGraph()
        g.nodes = dict(self.nodes)
        g.wires = dict(self.wires)
        g._next_id = self._next_id
        return g

    def canonical(self) -> str:
        remap: dict[int, int] = {}
        order: list[int] = []

        def visit(nid: int):
            if nid in remap:
                return
            remap[nid] = len(order)
            order.append(nid)
            for idx in range(PORTS[self.nodes[nid].kind]):
                other = self.wires.get((nid, idx))
                if other is not None:
                    visit(other[0])

        for nid in sorted(self.nodes):
            visit(nid)

        lines: list[str] = []
        for nid in order:
            o = self.nodes[nid]
            rn = remap[nid]
            for idx in range(PORTS[o.kind]):
                other = self.wires.get((nid, idx))
                tgt = "." if other is None else f"{remap[other[0]]}:{other[1]}"
                lines.append(f"{rn}:{o.kind}:{o.value}:{idx}->{tgt}")
        return "\n".join(sorted(lines))

    def hash(self) -> str:
        return "sha256:" + hashlib.sha256(
            self.canonical().encode("utf-8")).hexdigest()[:24]
