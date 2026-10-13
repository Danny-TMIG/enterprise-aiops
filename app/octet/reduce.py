from __future__ import annotations

from app.octet.graph import OctetGraph
from app.octet.octet import D, E, G


def _annihilate(g: OctetGraph, n1: int, n2: int) -> None:
    g.detach((n1, 0))
    a0_1 = g.detach((n1, 1)); a1_1 = g.detach((n1, 2))
    a0_2 = g.detach((n2, 1)); a1_2 = g.detach((n2, 2))
    del g.nodes[n1]; del g.nodes[n2]
    g.wire(a0_1, a0_2)
    g.wire(a1_1, a1_2)


def _erase_gd(g: OctetGraph, nid: int) -> None:
    a0 = g.detach((nid, 1)); a1 = g.detach((nid, 2))
    del g.nodes[nid]
    e1 = g.new_node(E); e2 = g.new_node(E)
    g.wire((e1, 0), a0); g.wire((e2, 0), a1)


def _commute(g: OctetGraph, ng: int, nd: int, val: int) -> None:
    """γ[a]-δ[a] → 4 new nodes. Half the value is preserved on the
    new G nodes, the D nodes take the low/high nibble pair."""
    g.detach((ng, 0))
    a = g.detach((ng, 1)); b = g.detach((ng, 2))
    c = g.detach((nd, 1)); d = g.detach((nd, 2))
    del g.nodes[ng]; del g.nodes[nd]

    lo = val & 0x0F
    hi = (val >> 4) & 0x0F

    d1 = g.new_node(D, hi); g1 = g.new_node(G, hi)
    d2 = g.new_node(D, lo); g2 = g.new_node(G, lo)

    g.wire((d1, 1), a); g.wire((g1, 1), c)
    g.wire((d2, 1), b); g.wire((g2, 1), d)
    g.wire((d1, 2), (g1, 2))
    g.wire((d2, 2), (g2, 2))
    g.wire((d1, 0), (g1, 0))
    g.wire((d2, 0), (g2, 0))


def step(g: OctetGraph) -> str:
    """One reduction. Returns the rule name or 'stuck'."""
    for n1, n2 in g.active_pairs():
        o1, o2 = g.nodes[n1], g.nodes[n2]
        k1, k2 = o1.kind, o2.kind

        if k1 == G and k2 == G:
            if o1.value == o2.value:
                _annihilate(g, n1, n2)
                return "G-G-annihilate"
            # mismatch → stuck; do not fire
            continue
        if k1 == D and k2 == D:
            if o1.value == o2.value:
                _annihilate(g, n1, n2)
                return "D-D-annihilate"
            continue
        if k1 == E and k2 == E:
            g.detach((n1, 0))
            del g.nodes[n1]; del g.nodes[n2]
            return "E-E-annihilate"
        if {k1, k2} == {G, D}:
            gN, dN = (n1, n2) if k1 == G else (n2, n1)
            if g.nodes[gN].value == g.nodes[dN].value:
                _commute(g, gN, dN, g.nodes[gN].value)
                return "G-D-commute"
            continue
        if {k1, k2} == {G, E}:
            gN, eN = (n1, n2) if k1 == G else (n2, n1)
            g.detach((eN, 0))
            del g.nodes[eN]
            _erase_gd(g, gN)
            return "G-E-erase"
        if {k1, k2} == {D, E}:
            dN, eN = (n1, n2) if k1 == D else (n2, n1)
            g.detach((eN, 0))
            del g.nodes[eN]
            _erase_gd(g, dN)
            return "D-E-erase"
    return "stuck"


def normalise(g: OctetGraph, max_steps: int = 10_000
              ) -> tuple[OctetGraph, int, list[str]]:
    n = 0
    trace: list[str] = []
    while n < max_steps:
        rule = step(g)
        if rule == "stuck":
            break
        trace.append(rule)
        n += 1
    return g, n, trace
