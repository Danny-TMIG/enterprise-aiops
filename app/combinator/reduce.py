"""The six interaction rules.

  γ-γ  cross          (annihilation)
  δ-δ  cross          (annihilation)
  ε-ε  annihilate     (annihilation)
  γ-δ  commute        (commutation → 4 new nodes)
  γ-ε  erase          (γ's two aux ports get ε's)
  δ-ε  erase          (δ's two aux ports get ε's)

Each rule touches only the two participants and their aux wires.
No global state is consulted. No history. No floats.
"""
from __future__ import annotations

from app.combinator.graph import D, E, G, Graph


# ── annihilations ───────────────────────────────────────────────
def _annihilate(g: Graph, n1: int, n2: int) -> None:
    """Two 3-port nodes of the same kind meet principal-to-principal.
    Cross-wire their auxiliaries and remove both."""
    g.detach((n1, 0))
    a0_1 = g.detach((n1, 1))
    a1_1 = g.detach((n1, 2))
    a0_2 = g.detach((n2, 1))
    a1_2 = g.detach((n2, 2))
    del g.nodes[n1]
    del g.nodes[n2]
    g.wire(a0_1, a0_2)
    g.wire(a1_1, a1_2)


def rule_gg(g: Graph, n1: int, n2: int) -> None:
    _annihilate(g, n1, n2)


def rule_dd(g: Graph, n1: int, n2: int) -> None:
    _annihilate(g, n1, n2)


def rule_ee(g: Graph, n1: int, n2: int) -> None:
    g.detach((n1, 0))
    del g.nodes[n1]
    del g.nodes[n2]


# ── commutation γ-δ → 4 new nodes ──────────────────────────────
def rule_gd(g: Graph, ng: int, nd: int) -> None:
    """γ (aux a, b) meets δ (aux c, d).
       Produces 4 nodes: δ₁, γ₁, δ₂, γ₂ wired as a 2×2 lattice.
       Two new γ-δ active pairs are created."""
    g.detach((ng, 0))
    a = g.detach((ng, 1))
    b = g.detach((ng, 2))
    c = g.detach((nd, 1))
    d = g.detach((nd, 2))
    del g.nodes[ng]
    del g.nodes[nd]

    d1 = g.new_node(D); g1 = g.new_node(G)
    d2 = g.new_node(D); g2 = g.new_node(G)

    # external
    g.wire((d1, 1), a)
    g.wire((g1, 1), c)
    g.wire((d2, 1), b)
    g.wire((g2, 1), d)
    # internal aux wires (the "sharing")
    g.wire((d1, 2), (g1, 2))
    g.wire((d2, 2), (g2, 2))
    # new active pairs
    g.wire((d1, 0), (g1, 0))
    g.wire((d2, 0), (g2, 0))


# ── erasures ────────────────────────────────────────────────────
def rule_ge(g: Graph, ng: int, ne: int) -> None:
    """γ with ε as principal partner: two new ε's on γ's aux ports."""
    g.detach((ng, 0))
    a0 = g.detach((ng, 1))
    a1 = g.detach((ng, 2))
    del g.nodes[ng]
    del g.nodes[ne]
    e1 = g.new_node(E); e2 = g.new_node(E)
    g.wire((e1, 0), a0)
    g.wire((e2, 0), a1)


def rule_de(g: Graph, nd: int, ne: int) -> None:
    g.detach((nd, 0))
    a0 = g.detach((nd, 1))
    a1 = g.detach((nd, 2))
    del g.nodes[nd]
    del g.nodes[ne]
    e1 = g.new_node(E); e2 = g.new_node(E)
    g.wire((e1, 0), a0)
    g.wire((e2, 0), a1)


# ── the reducer ─────────────────────────────────────────────────
def step(g: Graph) -> bool:
    """Perform one reduction. Return True if a rule fired."""
    for n1, n2 in g.active_pairs():
        k1, k2 = g.nodes[n1], g.nodes[n2]
        pair = frozenset((k1, k2))
        if pair == {G}:
            rule_gg(g, n1, n2)
        elif pair == {D}:
            rule_dd(g, n1, n2)
        elif pair == {E}:
            rule_ee(g, n1, n2)
        elif pair == {G, D}:
            if k1 == G: rule_gd(g, n1, n2)
            else:       rule_gd(g, n2, n1)
        elif pair == {G, E}:
            if k1 == G: rule_ge(g, n1, n2)
            else:       rule_ge(g, n2, n1)
        elif pair == {D, E}:
            if k1 == D: rule_de(g, n1, n2)
            else:       rule_de(g, n2, n1)
        else:
            continue
        return True
    return False


def normalise(g: Graph, max_steps: int = 10_000) -> tuple[Graph, int, bool]:
    """Reduce to normal form. Return (graph, steps, terminated)."""
    n = 0
    while n < max_steps:
        if not step(g):
            return g, n, True
        n += 1
    return g, n, False


def normalise_with_trace(g: Graph,
                         max_steps: int = 10_000
                         ) -> tuple[Graph, list[tuple[int, str]]]:
    """Reduce and record (step, node_count) at each step."""
    trace = [(0, len(g.nodes))]
    n = 0
    while n < max_steps:
        if not step(g):
            break
        n += 1
        trace.append((n, len(g.nodes)))
    return g, trace
