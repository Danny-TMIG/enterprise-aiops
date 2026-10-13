"""Content addressing on normal forms.

The identity of a graph is the SHA-256 of its canonical string
form. Two graphs that reduce to the same normal form have the same
hash. No canonicalization of the input is required, because the
normal form is already canonical.
"""
from __future__ import annotations

import hashlib
from typing import Any

from app.combinator.graph import Graph
from app.combinator.reduce import normalise


def hash_graph(g: Graph) -> str:
    canon = g.to_canonical()
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


def normal_form_id(g: Graph,
                   max_steps: int = 10_000
                   ) -> dict[str, Any]:
    ng, n, terminated = normalise(g.copy(), max_steps=max_steps)
    return {
        "normal_form_hash": hash_graph(ng),
        "steps": n,
        "terminated": terminated,
        "nodes_in": len(g.nodes),
        "nodes_out": len(ng.nodes),
    }
