"""Self-similarity: every level of T is itself a topos.

  * T           is a topos
  * Sub(T)      (subobjects)          is a topos
  * Skill(T)    (skills from SIGNATURE) is a topos
  * Agent(T)    (agents from the mesh)  is a topos

They all share the same Ω and the same terminal 1. The embedding
`embed` lifts any finite category C into T's shape by adding 1, Ω,
and the classifier ⊤.
"""
from __future__ import annotations

from typing import Any

from app.topos.category import Category, Object
from app.topos.topos import Topos


def embed(C: Category) -> Topos:
    """Lift a finite category into a topos with the same Ω."""
    T = Topos(name=f"T({C.name})")
    for o in C.objects.values():
        if o.id not in T.objects:
            T.add(Object(o.id, o.kind, dict(o.data)))
    for m in C.morphisms:
        if m.name == "⊤":
            continue
        T.morphisms.append(m)
    return T


def is_topos(C: Category) -> bool:
    return isinstance(C, Topos) and C.is_topos()


def lift_axes(T: Topos) -> dict[str, Topos]:
    """Every axis is itself a topos, sharing T's Ω."""
    from app.topos.axes import Axes
    axes = Axes(T)
    out: dict[str, Topos] = {}
    for name, c in (("Forward", axes.F),
                    ("Inverse", axes.G),
                    ("Relational", axes.R)):
        Ta = embed(c)
        out[name] = Ta
    return out


class SelfSimilarity:
    """The whole point: one shape, three axes, all levels."""

    def __init__(self, T: Topos) -> None:
        self.T = T
        self.axes = lift_axes(T)

    def all_topoi(self) -> dict[str, Topos]:
        return {"T": self.T, **self.axes}

    def verify(self) -> dict[str, Any]:
        checks: dict[str, Any] = {}
        for name, Ta in self.all_topoi().items():
            checks[name] = Ta.is_topos()
        # shared classifier
        checks["shared_omega"] = all(
            Ta.classifier.omega_id == "Ω"
            for Ta in self.all_topoi().values()
        )
        checks["all_ok"] = all(checks.values())
        return checks

    def to_dict(self) -> dict[str, Any]:
        return {
            "topoi": {n: Ta.stats() for n, Ta in self.all_topoi().items()},
            "verification": self.verify(),
        }
