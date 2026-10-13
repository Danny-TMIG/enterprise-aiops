"""Port-based graph for interaction combinators.

A node has 3 ports for γ and δ, 1 port for ε.
Ports are (node_id, port_index).  Index 0 = principal, 1 = aux0, 2 = aux1.
Wires is a symmetric dict: port -> port.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

Port = tuple[int, int]      # (node_id, port_index)
G = "g"                     # γ  (constructor)
D = "d"                     # δ  (duplicator)
E = "e"                     # ε  (eraser)

_NUM_PORTS = {G: 3, D: 3, E: 1}


@dataclass
class Graph:
    nodes: dict[int, str] = field(default_factory=dict)
    wires: dict[Port, Port] = field(default_factory=dict)
    _next_id: int = 0

    # ── construction ────────────────────────────────────────────
    def new_node(self, kind: str) -> int:
        if kind not in _NUM_PORTS:
            raise ValueError(f"unknown kind: {kind}")
        nid = self._next_id
        self._next_id += 1
        self.nodes[nid] = kind
        return nid

    def wire(self, p1: Port | None, p2: Port | None) -> None:
        if p1 is None or p2 is None:
            return
        self.wires[p1] = p2
        self.wires[p2] = p1

    def detach(self, p: Port) -> Port | None:
        """Remove the wire at port p from both ends and return the
        other end, or None if p was not wired."""
        other = self.wires.pop(p, None)
        if other is not None:
            self.wires.pop(other, None)
        return other

    def kill(self, nid: int) -> None:
        """Remove a node and any wires attached to its ports."""
        if nid not in self.nodes:
            return
        for idx in range(_NUM_PORTS[self.nodes[nid]]):
            self.detach((nid, idx))
        del self.nodes[nid]

    # ── queries ─────────────────────────────────────────────────
    def active_pairs(self) -> Iterator[tuple[int, int]]:
        for nid, kind in list(self.nodes.items()):
            if kind == E:
                continue
            # ε has only a principal port; both γ and δ have principals
        for nid in list(self.nodes.keys()):
            p = (nid, 0)
            other = self.wires.get(p)
            if other is None or other[1] != 0:
                continue
            onid = other[0]
            if onid not in self.nodes or onid <= nid:
                continue
            yield nid, onid

    def copy(self) -> Graph:
        g = Graph()
        g.nodes = dict(self.nodes)
        g.wires = dict(self.wires)
        g._next_id = self._next_id
        return g

    def to_canonical(self) -> str:
        """Deterministic string form for hashing. Node ids are
        re-canonicalised by BFS from the smallest id."""
        # build adjacency on re-indexed ids
        remap: dict[int, int] = {}
        order: list[int] = []

        def visit(nid: int):
            if nid in remap:
                return
            remap[nid] = len(order)
            order.append(nid)
            for idx in range(_NUM_PORTS[self.nodes.get(nid, G)]):
                other = self.wires.get((nid, idx))
                if other is not None:
                    visit(other[0])

        for nid in sorted(self.nodes):
            visit(nid)

        lines: list[str] = []
        for nid in order:
            kind = self.nodes[nid]
            rn = remap[nid]
            for idx in range(_NUM_PORTS[kind]):
                other = self.wires.get((nid, idx))
                if other is None:
                    tgt = "."
                else:
                    tgt = f"{remap.get(other[0], '?')}:{other[1]}"
                lines.append(f"{rn}:{kind}:{idx}->{tgt}")
        return "\n".join(sorted(lines))
