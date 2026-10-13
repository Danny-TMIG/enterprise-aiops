"""MeshGraph — nodes is a dict keyed by id; edges is a list."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class MeshGraph:
    def __init__(self, *args, **kwargs):
        self.nodes: dict[str, Any] = {}
        self.edges: list[Any] = []

    def add(self, node) -> None:
        nid = getattr(node, "id", None) or f"node:{len(self.nodes)}"
        try:
            node.id = nid
        except Exception:
            pass
        self.nodes[nid] = node

    def add_edge(self, edge) -> None:
        self.edges.append(edge)

    def iter_nodes(self) -> Iterable[Any]:
        return iter(self.nodes.values())

    def iter_edges(self) -> Iterable[Any]:
        return iter(self.edges)

    def node_by_id(self, nid: str):
        return self.nodes.get(nid)

    def stats(self) -> dict[str, Any]:
        kinds: dict[str, int] = {}
        for n in self.nodes.values():
            k = getattr(n, "kind", "unknown")
            kinds[k] = kinds.get(k, 0) + 1
        return {"nodes": len(self.nodes), "edges": len(self.edges), "kinds": kinds}

    @property
    def graph(self) -> MeshGraph:
        return self
