"""A generic constraint grid."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

VarId = str
Coord = Tuple[int, int]
Cell = Coord


@dataclass
class Var:
    id: VarId
    domain: List[Any]
    coords: List[Coord] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Constraint:
    id: str
    scope: List[VarId]
    check: Callable[[Dict[VarId, Any]], bool]

    def satisfied(self, assignment: Dict[VarId, Any]) -> bool:
        try:
            return bool(self.check(assignment))
        except Exception:
            return False


@dataclass
class Grid:
    vars: Dict[VarId, Var] = field(default_factory=dict)
    constraints: List[Constraint] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

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
