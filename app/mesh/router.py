"""Node + route(intent, graph)."""
from __future__ import annotations

from typing import Any


class Node:
    def __init__(self, id: str = "", kind: str = "unknown", name: str = "",
                 file: str = "", line: int = 0, extra: list | None = None,
                 **kwargs):
        self.id = id
        self.kind = kind
        self.name = name or id
        self.file = file
        self.line = line
        self.extra = list(extra or [])
        for k, v in kwargs.items():
            setattr(self, k, v)


def _nodes(graph):
    n = getattr(graph, "nodes", {})
    return n.values() if isinstance(n, dict) else n


def route(intent: str, graph) -> list[dict[str, Any]]:
    tokens = [t for t in (intent or "").lower().split() if t]
    out: list[dict[str, Any]] = []
    for node in _nodes(graph):
        name = str(getattr(node, "name", "") or "")
        if not name:
            continue
        lname = name.lower()
        score = sum(1.0 for tok in tokens if tok in lname)
        if score > 0:
            out.append({
                "id": str(getattr(node, "id", "")),
                "name": name,
                "kind": str(getattr(node, "kind", "")),
                "file": str(getattr(node, "file", "")),
                "line": int(getattr(node, "line", 0) or 0),
                "score": float(score),
            })
    out.sort(key=lambda m: -m["score"])
    return out
