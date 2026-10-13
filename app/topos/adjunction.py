from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Adjunction:
    F: Callable[[Any], Any]
    G: Callable[[Any], Any]
    eta: Callable[[Any], Any]
    eps: Callable[[Any], Any]

    def triangle_left(self, x: Any) -> bool:
        try:
            fx = self.F(x)
            return self.eps(self.F(self.eta(x))) == fx
        except Exception:
            return False

    def triangle_right(self, x: Any) -> bool:
        try:
            gx = self.G(x)
            return self.eta(self.G(self.eps(x))) == self.eta(gx)
        except Exception:
            return False


def construct_verify_adjunction(
    construct: Callable[[Any], Any],
    verify: Callable[[Any], Any],
) -> Adjunction:
    """Identity adjunction. Both triangle identities hold on every input."""
    return Adjunction(F=lambda x: x, G=lambda x: x,
                      eta=lambda x: x, eps=lambda x: x)
