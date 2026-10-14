"""Typed relation graph for the sovereign node."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


@dataclass
class Node:
    id: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    predicate: str
    target: str


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | None = None) -> "Graph":
        data = json.loads((path or ROOT / "relations.json").read_text())
        nodes = {n["id"]: Node(n["id"], n["type"], n.get("properties", {})) for n in data["nodes"]}
        edges = [Edge(e["source"], e["predicate"], e["target"]) for e in data["edges"]]
        return cls(nodes=nodes, edges=edges)

    def out_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.source == node_id]

    def in_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.target == node_id]

    def walk(self, start: str, predicate: str) -> list[str]:
        return [e.target for e in self.out_edges(start) if e.predicate == predicate]

    def validate(self) -> list[str]:
        errs = []
        for e in self.edges:
            if e.source not in self.nodes:
                errs.append(f"edge source missing: {e.source}")
            if e.target not in self.nodes and not e.target.isdigit():
                errs.append(f"edge target missing: {e.target}")
        return errs


if __name__ == "__main__":
    g = Graph.load()
    print(f"nodes: {len(g.nodes)}  edges: {len(g.edges)}")
    errs = g.validate()
    print(f"validation errors: {len(errs)}")
    for e in errs:
        print(" ", e)
    print()
    for n in sorted(g.nodes):
        outs = g.out_edges(n)
        if outs:
            print(f"{n}:")
            for e in outs:
                print(f"  --{e.predicate}--> {e.target}")
