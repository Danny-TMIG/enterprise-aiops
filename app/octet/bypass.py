"""The bypass.

Rule-free reduction to a task graph. There is no op table. There is
no rule table. The task graph is *read off* the normal form of the
octet graph.

An emergent task is a connected sub-graph of the normal form whose
shape matches one of a small number of graph-shape predicates. The
predicates are not rules; they are functions of graph topology. New
languages add no predicates — they add shapes in the residue.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.octet.graph import OctetGraph
from app.octet.octet import PORTS, D, E, G
from app.octet.reduce import normalise


@dataclass
class EmergentTask:
    id: str
    shape: str
    nodes: int
    value_span: tuple[int, int]
    evidence: str


def _shapes(g: OctetGraph) -> list[EmergentTask]:
    """Read task shapes from a normal form. No rules. Only topology."""
    out: list[EmergentTask] = []
    # connected components again
    seen: set = set()
    idx = 0
    for nid in g.nodes:
        if nid in seen:
            continue
        comp_nodes = []
        stack = [nid]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp_nodes.append(u)
            for pidx in range(PORTS[g.nodes[u].kind]):
                other = g.wires.get((u, pidx))
                if other is not None and other[0] not in seen:
                    stack.append(other[0])

        kinds = [g.nodes[u].kind for u in comp_nodes]
        values = [g.nodes[u].value for u in comp_nodes]
        n = len(comp_nodes)

        if n == 1:
            shape = "atom"
        elif n == 2:
            shape = "pair"
        elif all(k == G for k in kinds):
            shape = f"chain[{n}]"
        elif all(k == D for k in kinds):
            shape = f"fanout[{n}]"
        elif kinds.count(E) == n:
            shape = f"empty[{n}]"
        elif kinds.count(G) and kinds.count(D):
            shape = f"mix[{kinds.count(G)}G{kinds.count(D)}D]"
        else:
            shape = f"unknown[{n}]"

        out.append(EmergentTask(
            id=f"et{idx}",
            shape=shape,
            nodes=n,
            value_span=(min(values) if values else 0,
                        max(values) if values else 0),
            evidence=f"component of {n} nodes",
        ))
        idx += 1
    return out


def bypass(g: OctetGraph, max_steps: int = 10_000
           ) -> tuple[OctetGraph, list[EmergentTask], int, list[str]]:
    """Reduce and read. No rules. No op table. Everything emergent."""
    ng, n, trace = normalise(g.copy(), max_steps=max_steps)
    tasks = _shapes(ng)
    return ng, tasks, n, trace
