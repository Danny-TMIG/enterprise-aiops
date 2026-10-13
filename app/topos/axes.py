"""The three axes, each a full subcategory of T.

  Forward   : construct       intent  ↦ spec ↦ artifact
  Inverse   : verify          artifact ↦ scan ↦ proof ↦ kernel ↦ object
  Relational: bind            artifact × artifact ↦ composition

All three share the same objects and morphisms from T. The axes are
just views — distinguished sub-categories with a selected set of
arrows.
"""
from __future__ import annotations

from typing import Any

from app.topos.category import Category
from app.topos.topos import Topos


class Forward(Category):
    """Objects: intent, spec, artifact. Arrows: the constructive path."""
    def __init__(self, T: Topos) -> None:
        super().__init__("Forward")
        self.T = T
        self._select(["intent", "spec", "artifact"])
        self._links([
            ("intent", "spec", "draft"),
            ("spec", "artifact", "generate"),
        ])

    def _select(self, ids: list[str]) -> None:
        for i in ids:
            if i in self.T.objects:
                self.add(self.T.objects[i])

    def _links(self, pairs: list[tuple]) -> None:
        for src, dst, name in pairs:
            for m in self.T.morphisms:
                if m.src == src and m.dst == dst and m.name == name:
                    self.morphisms.append(m)
                    break


class Inverse(Category):
    """Objects: artifact, proof. Arrows: the verification path."""
    def __init__(self, T: Topos) -> None:
        super().__init__("Inverse")
        self.T = T
        self._select(["artifact", "proof"])
        self._links([
            ("artifact", "proof", "verify"),
        ])

    def _select(self, ids: list[str]) -> None:
        for i in ids:
            if i in self.T.objects:
                self.add(self.T.objects[i])

    def _links(self, pairs: list[tuple]) -> None:
        for src, dst, name in pairs:
            for m in self.T.morphisms:
                if m.src == src and m.dst == dst and m.name == name:
                    self.morphisms.append(m)
                    break


class Relational(Category):
    """Objects: artifacts / capabilities / agents. Arrows: bindings."""
    def __init__(self, T: Topos) -> None:
        super().__init__("Relational")
        self.T = T
        for o in T.objects.values():
            if o.kind in ("artifact", "capability", "agent", "skill"):
                self.add(o)
        for m in T.morphisms:
            if m.meta.get("binding"):
                self.morphisms.append(m)


class Axes:
    def __init__(self, T: Topos) -> None:
        self.T = T
        self.F = Forward(T)
        self.G = Inverse(T)
        self.R = Relational(T)

    def stats(self) -> dict[str, Any]:
        return {
            "Forward": self.F.stats(),
            "Inverse": self.G.stats(),
            "Relational": self.R.stats(),
        }

    def share_omega(self) -> bool:
        """All three axes inherit the same subobject classifier."""
        for c in (self.F, self.G, self.R):
            if "Ω" not in c.objects:
                # axes may not select Ω as an object; but they must
                # still see the same terminal/classifier from T.
                pass
        return (self.T.classifier.omega_id == "Ω"
                and self.T.classifier.terminal_id == "1")
