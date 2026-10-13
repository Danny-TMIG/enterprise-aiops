"""Self-application and the fixed point.

The self-referential loop in interaction combinators is:

  1. Build a graph G.
  2. Reduce G to its normal form G*.
  3. Hash G*.
  4. Encode the hash bytes as a graph G'.
  5. Reduce G'.
  6. If hash(reduce(G')) == hash(G'), the reduction is a fixed point
     of itself.

The "encode bytes as graph" step is the identity up to the encoding
map. We define a canonical encoder: bytes → chain of ε nodes
(erasure-only graph). The encoder is deterministic, so the loop is
deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.combinator.canonical import hash_graph
from app.combinator.graph import E, G, Graph
from app.combinator.reduce import normalise


def bytes_to_graph(b: bytes) -> Graph:
    """Deterministic encoding: each byte becomes a small γ-δ-ε
    gadget. The graph's normal form is itself (no active pairs)."""
    g = Graph()
    prev_principal = None
    for byte in b:
        n = g.new_node(G)
        g.new_node(E)  # attached ε
        # attach ε to γ aux0
        eid = g._next_id - 1
        g.wire((n, 1), (eid, 0))
        # chain principal
        if prev_principal is not None:
            g.wire(prev_principal, (n, 0))
        prev_principal = (n, 2)  # dangling
    return g


@dataclass
class FixedPoint:
    iterations: int
    stable: bool
    hashes: list[str] = field(default_factory=list)
    steps: list[int] = field(default_factory=list)
    terminated: list[bool] = field(default_factory=list)


def self_apply(seed: Graph, max_iterations: int = 6) -> FixedPoint:
    fp = FixedPoint(iterations=0, stable=False)
    g = seed
    prev_hash = None
    for i in range(max_iterations):
        ng, steps, terminated = normalise(g.copy())
        h = hash_graph(ng)
        fp.hashes.append(h)
        fp.steps.append(steps)
        fp.terminated.append(terminated)
        fp.iterations = i + 1

        if prev_hash == h and terminated:
            fp.stable = True
            break

        prev_hash = h
        # feed the hash bytes back as a graph
        raw = bytes.fromhex(h.split(":", 1)[1])
        g = bytes_to_graph(raw[:32])       # 32 bytes → 32 gadgets
    return fp
