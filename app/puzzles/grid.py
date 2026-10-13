"""A generic constraint grid."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

VarId = str
Coord = tuple[int, int]
Cell = Coord


@dataclass
class Var:
    id: VarId
    domain: list[Any]
    coords: list[Coord] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Constraint:
    id: str
    scope: list[VarId]
    check: Callable[[dict[VarId, Any]], bool]

    def satisfied(self, assignment: dict[VarId, Any]) -> bool:
        try:
            return bool(self.check(assignment))
        except Exception:
            return False


@dataclass
class Grid:
    vars: dict[VarId, Var] = field(default_factory=dict)
    constraints: list[Constraint] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def add_var(self, v: Var) -> None:
        self.vars[v.id] = v

    def add_constraint(self, c: Constraint) -> None:
        self.constraints.append(c)

    def summary(self) -> dict:
        return {
            "n_vars": len(self.vars),
            "n_constraints": len(self.constraints),
            "total_domain": sum(len(v.domain) for v in self.vars.values()),
            "meta": self.meta,
        }
