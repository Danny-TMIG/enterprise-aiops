"""Walk from a module to its terminal residual Ω."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.residual import register as R
from app.residual.anchors import ANCHORS, OMEGA, anchors_for


@dataclass
class Chain:
    module: str
    residuals: list[R.Residual] = field(default_factory=list)
    terminal: str = OMEGA
    valid: bool = True
    missing: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "residuals": [
                {"id": r.id, "class": r.class_name,
                 "name": r.name, "source": r.source, "arity": str(r.arity)}
                for r in self.residuals
            ],
            "terminal": self.terminal,
            "valid": self.valid,
            "missing": self.missing,
        }


def terminate(module: str) -> Chain:
    ids = anchors_for(module)
    chain = Chain(module=module)
    for rid in ids:
        try:
            chain.residuals.append(R.get(rid))
        except KeyError:
            chain.missing.append(rid)
            chain.valid = False
    if not R.is_valid(OMEGA):
        chain.valid = False
    return chain


def terminate_all() -> list[Chain]:
    return [terminate(m) for m in sorted(ANCHORS)]


def render(chain: Chain) -> str:
    lines = [f"── {chain.module} ──"]
    for r in chain.residuals:
        mark = "⊘" if r.arity == 0 else "⟳"
        lines.append(
            f"  {mark} {r.id:6s} {r.class_name:22s} {r.name}"
        )
    if chain.missing:
        lines.append(f"  ! missing: {chain.missing}")
    lines.append(f"  ⊢ → {chain.terminal}")
    return "\n".join(lines)
