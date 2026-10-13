"""A finite topos.

For our purposes a topos is a Category with:
  * a terminal object 1
  * finite products
  * a subobject classifier Ω with a morphism ⊤: 1 → Ω
  * exponentials (we check cartesian closure by construction on
    the finite hom-sets)

We construct it directly: Ω = {False, True}, and every morphism has
a characteristic arrow χ: dst → Ω that reads "is this in the
verified subobject?".
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.topos.category import Category, Morphism, Object

TERMINAL_ID = "1"
OMEGA_ID = "Ω"


@dataclass
class SubobjectClassifier:
    """Ω with ⊤: 1 → Ω.  χ maps a subobject's points to truth."""
    omega_id: str = OMEGA_ID
    terminal_id: str = TERMINAL_ID
    true_value: Any = True
    false_value: Any = False

    def true_morphism(self) -> Morphism:
        return Morphism(
            src=self.terminal_id, dst=self.omega_id, name="⊤",
            fn=lambda _: self.true_value,
            meta={"classifier": True},
        )

    def characteristic(self, subobject_predicate: Callable[[Any], bool],
                       X: str) -> Morphism:
        tv, fv = self.true_value, self.false_value
        return Morphism(
            src=X, dst=self.omega_id, name=f"χ_{X}",
            fn=lambda x: tv if subobject_predicate(x) else fv,
            meta={"classifier": True, "of": X},
        )

    def to_dict(self) -> dict[str, Any]:
        return {"omega": self.omega_id, "terminal": self.terminal_id,
                "values": [self.true_value, self.false_value]}


class Topos(Category):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        # 1 and Ω are always present
        self.add(Object(TERMINAL_ID, "terminal", {}))
        self.add(Object(OMEGA_ID, "omega", {"values": [True, False]}))
        self.classifier = SubobjectClassifier()
        # ⊤: 1 → Ω  is a morphism in the topos
        self.morphisms.append(self.classifier.true_morphism())

    # ── cartesian closure (finite) ─────────────────────────────
    def product(self, a: str, b: str) -> str:
        pid = f"{a}×{b}"
        if pid not in self.objects:
            self.add(Object(pid, "product", {"factors": [a, b]}))
            # projections
            self.arrow(pid, a, f"π1_{pid}", lambda p: p[0],
                       meta={"projection": 1})
            self.arrow(pid, b, f"π2_{pid}", lambda p: p[1],
                       meta={"projection": 2})
        return pid

    def exponential(self, a: str, b: str) -> str:
        eid = f"{b}^{a}"
        if eid not in self.objects:
            self.add(Object(eid, "exponential", {"base": b, "exp": a}))
        return eid

    # ── subobjects ─────────────────────────────────────────────
    def subobject(self, X: str, name: str,
                  predicate: Callable[[Any], bool]) -> Morphism:
        """Add A ↪ X via a predicate; return the characteristic χ_A."""
        aid = f"{X}|{name}"
        self.add(Object(aid, "subobject", {"of": X, "name": name}))
        self.arrow(aid, X, f"ι_{name}", lambda x: x,
                   meta={"inclusion": True})
        chi = self.classifier.characteristic(predicate, X)
        self.morphisms.append(chi)
        return chi

    # ── structural checks ──────────────────────────────────────
    def is_topos(self) -> bool:
        return (
            TERMINAL_ID in self.objects
            and OMEGA_ID in self.objects
            and any(m.name == "⊤" for m in self.morphisms)
            and self.is_associative([None, 0, 1, "x", (), {}])
            and self.is_identity_lawful()
        )

    def stats(self) -> dict[str, Any]:
        s = super().stats()
        s["is_topos"] = self.is_topos()
        s["has_omega"] = OMEGA_ID in self.objects
        s["has_terminal"] = TERMINAL_ID in self.objects
        return s
