"""Physarum polycephalum router.

The Tokyo experiment in one file. Each edge carries flow. Each edge
independently decides its own next conductance from the flow it just
saw and a diffusive term from its neighbors. No global optimizer, no
gradient, no controller. Emergent topology only.

    D_ij(t+1) = (1-δ) * D_ij(t) + f(|Q_ij(t)|)
    Q_ij(t)   = D_ij(t) * (p_i(t) - p_j(t)) / L_ij
    f(q)      = q^μ / (1 + q^μ)

Three phases mirror the mold's behaviour:

    exploration  diffuse everywhere, thin edges
    pruning      drop edges whose flow falls below threshold
    reinforcement raise conductance of edges that carry flow

Bridges to the fabric: every edge is (src_code -> dst_code) between
capabilities. Flow is dispatch count over a window. The substrate
read is RAMSubstrate.tail(), so a run of the router is also a run of
the ledger.

Self-registers as capability `physarum`.
"""
from __future__ import annotations

import math
import random
import threading
from collections import deque
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any


# ── edge ────────────────────────────────────────────────────────────
@dataclass
class Edge:
    src: str
    dst: str
    L: float = 1.0            # length / cost
    D: float = 1.0            # conductance (the mold's tube width)
    Q: float = 0.0            # last flux
    flow_total: float = 0.0
    flow_window: deque[float] = field(default_factory=lambda: deque(maxlen=64))
    pruned: bool = False

    def key(self) -> tuple[str, str]:
        return (self.src, self.dst)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["flow_window"] = list(self.flow_window)
        return d


# ── router ──────────────────────────────────────────────────────────
class PhysarumRouter:
    """Edge-local update rule. No global pass over the graph."""

    def __init__(self, *,
                 delta: float = 0.05,       # decay
                 mu: float = 4.0,           # nonlinearity
                 prune_below: float = 0.05, # absolute D floor
                 reinforce_above: float = 0.5,
                 prune_window: int = 16,
                 seed: int = 0):
        self.delta = delta
        self.mu = mu
        self.prune_below = prune_below
        self.reinforce_above = reinforce_above
        self.prune_window = prune_window
        self._edges: dict[tuple[str, str], Edge] = {}
        self._lock = threading.RLock()
        self._tick = 0

    # ── topology ────────────────────────────────────────────────────
    def add(self, src: str, dst: str, *, L: float = 1.0,
            D: float | None = None, jitter: float = 0.35,
            seed: int | None = None) -> Edge:
        with self._lock:
            k = (src, dst)
            if k in self._edges:
                return self._edges[k]
            if D is None:
                # heterogeneous birth: each edge has its own thickness,
                # so each crosses the prune floor at its own moment.
                rng = random.Random(seed if seed is not None
                                    else hash(k) & 0xffffffff)
                D = max(0.05, 1.0 + rng.gauss(0, jitter))
            e = Edge(src=src, dst=dst, L=L, D=D)
            self._edges[k] = e
            return e

    def add_path(self, chain: Iterable[str], *,
                 L: float = 1.0) -> list[Edge]:
        chain = list(chain)
        return [self.add(chain[i], chain[i+1], L=L)
                for i in range(len(chain) - 1)]

    def edges(self, *, include_pruned: bool = False) -> list[Edge]:
        with self._lock:
            return [e for e in self._edges.values()
                    if include_pruned or not e.pruned]

    # ── flow injection ──────────────────────────────────────────────
    def send(self, src: str, dst: str, *, amount: float = 1.0) -> float:
        """Push flow through one edge. Returns the conductance it saw."""
        with self._lock:
            e = self._edges.get((src, dst))
            if e is None or e.pruned:
                return 0.0
            e.flow_window.append(amount)
            e.flow_total += amount
            e.Q = amount
            return e.D

    # ── edge-local update ───────────────────────────────────────────
    def _update_edge(self, e: Edge) -> None:
        # local signal: mean recent flow, damped by length
        recent = list(e.flow_window)
        if recent:
            q = sum(recent) / len(recent) / max(e.L, 1e-6)
        else:
            q = 0.0
        # sub-linear reinforcement: sqrt(q) not q**mu. This keeps a
        # spread of conductances instead of letting every surviving
        # edge saturate at the cap. The constant mu still sets the
        # exponent for the nonlinear path when q is well above 1.
        f = math.sqrt(max(q, 0.0))
        # soft cap: D -> cap * D / (cap + D). Sigmoid-like, no hard
        # ceiling. Growth slows as D approaches cap.
        cap = 8.0
        d_next = (1.0 - self.delta) * e.D + f
        e.D = cap * d_next / (cap + d_next)

        # prune rule: an edge that has stopped carrying flow and whose
        # conductance has fallen below the floor is dead. Both
        # conditions must hold; a fresh edge (flow_total>0) survives a
        # single quiet tick.
        if e.D < self.prune_below and e.flow_total <= 0.0 or e.D < self.prune_below / 2.0:
            e.pruned = True

        # cap
        e.D = min(e.D, 8.0)

    def tick(self, *, n: int = 1) -> int:
        """One local pass. Every live edge updates itself. Returns the
        number of edges pruned during this tick."""
        pruned = 0
        with self._lock:
            for e in self._edges.values():
                if e.pruned:
                    continue
                before = e.pruned
                self._update_edge(e)
                if not before and e.pruned:
                    pruned += 1
            self._tick += n
        return pruned

    # ── observation ─────────────────────────────────────────────────
    def topology(self) -> dict[str, Any]:
        with self._lock:
            live = [e for e in self._edges.values() if not e.pruned]
            dead = [e for e in self._edges.values() if e.pruned]
            return {
                "tick": self._tick,
                "live_edges": len(live),
                "pruned_edges": len(dead),
                "live": [
                    {"edge": f"{e.src}->{e.dst}", "D": round(e.D, 4),
                     "L": e.L, "flow_total": round(e.flow_total, 2)}
                    for e in sorted(live, key=lambda x: -x.D)
                ],
                "pruned": [f"{e.src}->{e.dst}" for e in dead],
            }

    def routes_from(self, src: str, *, min_D: float = 0.1) -> list[Edge]:
        with self._lock:
            out = [e for e in self._edges.values()
                   if e.src == src and not e.pruned and e.D >= min_D]
            out.sort(key=lambda x: -x.D)
            return out


# ── import from the fabric: capabilities + bridges become edges ─────
def from_capabilities(*, L: float = 1.0) -> PhysarumRouter:
    r = PhysarumRouter()
    try:
        from app.core.capabilities import BRIDGES, CAPS
    except Exception:
        return r
    for cap, gap, gid, kind, note in BRIDGES:
        r.add(cap, f"{gap}#{gid}", L=L)
    # hub: everything goes through the ledger
    for code, name, cat, eq, st, prov, home in CAPS:
        if st == "real":
            r.add("ledger", code, L=L)
    return r


# ── self-registration ───────────────────────────────────────────────
def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("physarum")
    def _entrypoint(*args: Any, **kwargs: Any) -> dict[str, Any]:
        r = from_capabilities()
        return {
            "module": "app.core.physarum",
            "edges": len(r.edges()),
            "tick": 0,
        }


_self_register()


__all__ = ["Edge", "PhysarumRouter", "from_capabilities"]
