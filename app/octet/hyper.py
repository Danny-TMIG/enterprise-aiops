"""Hyper-decomposition.

Split an octet graph into sub-graphs by connected component of
"kind+value". Reduce each sub-graph. The decomposition is
recursive: sub-graphs that still have active pairs are decomposed
again until each fragment is either reduced or stuck.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.octet.graph import OctetGraph
from app.octet.octet import PORTS
from app.octet.reduce import normalise


@dataclass
class Fragment:
    depth: int
    graph: OctetGraph
    steps: int
    terminated: bool
    trace: list[str] = field(default_factory=list)

    @property
    def hash(self) -> str:
        return self.graph.hash()


def _components(g: OctetGraph) -> list[OctetGraph]:
    """Split into connected components via wires."""
    seen: set = set()
    out: list[OctetGraph] = []
    for nid in g.nodes:
        if nid in seen:
            continue
        comp = OctetGraph()
        remap: dict[int, int] = {}
        stack = [nid]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            remap[u] = comp.new_node(g.nodes[u].kind, g.nodes[u].value)
            for idx in range(PORTS[g.nodes[u].kind]):
                other = g.wires.get((u, idx))
                if other is not None and other[0] not in seen:
                    stack.append(other[0])
        for u in remap:
            for idx in range(PORTS[g.nodes[u].kind]):
                other = g.wires.get((u, idx))
                if other is None:
                    continue
                v, vidx = other
                if u < v and v in remap:
                    comp.wire((remap[u], idx), (remap[v], vidx))
        out.append(comp)
    return out


class HyperDecomposer:
    def __init__(self, max_depth: int = 6, max_steps: int = 5_000):
        self.max_depth = max_depth
        self.max_steps = max_steps
        self.fragments: list[Fragment] = []

    def decompose(self, g: OctetGraph, depth: int = 0) -> None:
        comps = _components(g)
        for comp in comps:
            if len(comp.nodes) <= 1:
                self.fragments.append(Fragment(
                    depth=depth, graph=comp, steps=0,
                    terminated=True, trace=["trivial"],
                ))
                continue
            ng, n, trace = normalise(comp.copy(),
                                     max_steps=self.max_steps)
            terminated = (trace and trace[-1] != "stuck") or len(ng.nodes) <= 1
            frag = Fragment(depth=depth, graph=ng, steps=n,
                            terminated=terminated, trace=trace)
            self.fragments.append(frag)
            # recurse into a fragment that is not a single component
            if depth < self.max_depth and len(_components(ng)) > 1:
                self.decompose(ng, depth + 1)

    def summary(self) -> dict:
        return {
            "fragments": len(self.fragments),
            "by_depth": _count_by(self.fragments, "depth"),
            "terminated": sum(1 for f in self.fragments if f.terminated),
            "stuck": sum(1 for f in self.fragments if not f.terminated),
            "total_steps": sum(f.steps for f in self.fragments),
        }


def _count_by(items, attr):
    out: dict[int, int] = {}
    for it in items:
        k = getattr(it, attr)
        out[k] = out.get(k, 0) + 1
    return out
