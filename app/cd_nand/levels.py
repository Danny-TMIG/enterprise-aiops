"""The ten levels of the tower.

Each level = one formal system. Each level has:
    - a basis (the CD basis at that depth)
    - a set of primitive operations
    - a property that was lost in the doubling
    - a specification of the invariant preserved

The tower as a whole is the sequence.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from app.cd_nand.cayley import BOOL_ALG, CD, Alg, cd_basis, cd_one, cd_zero
from app.cd_nand.nand import NAND


# ────────────────────────────────────────────────────────────────
# Level specifications
# ────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class LevelSpec:
    index: int
    name: str
    dimension: int
    primitives: tuple[str, ...]
    loses: str
    invariant: str


LEVELS: tuple[LevelSpec, ...] = (
    LevelSpec(0, "Boolean logic", 1,
              ("nand",),
              "order",   # already gone
              "every Boolean is a NAND tree"),
    LevelSpec(1, "Lambda calculus", 2,
              ("lambda", "apply", "var"),
              "commutativity",
              "beta-reduction is confluent"),
    LevelSpec(2, "Combinatory logic", 4,
              ("S", "K"),
              "associativity",
              "S and K generate every closed term"),
    LevelSpec(3, "Turing machine", 8,
              ("read", "write", "move", "state"),
              "alternativity",
              "each transition is deterministic"),
    LevelSpec(4, "Pi calculus", 16,
              ("send", "recv", "par", "new"),
              "no zero divisors",
              "reduction is preserved under parallel composition"),
    LevelSpec(5, "Interaction combinators", 32,
              ("gamma", "delta", "epsilon"),
              "no ordered field",
              "each rule is local and pairs two nodes"),
    LevelSpec(6, "Cellular automata", 64,
              ("state", "neighbor", "update-rule"),
              "no division algebra",
              "each cell updates from its 1-neighborhood"),
    LevelSpec(7, "Category theory", 128,
              ("id", "compose"),
              "no alternativity of any kind",
              "composition is associative, identity is two-sided"),
    LevelSpec(8, "Quantum mechanics", 256,
              ("position", "momentum", "hamiltonian"),
              "no commutativity of observables",
              "the commutator is i*hbar on conjugate pairs"),
    LevelSpec(9, "General computation", 512,
              ("state", "input", "transition"),
              "no algebraic identity left",
              "state_{t+1} = F(state_t, input_t) for any F"),
)

LEVEL_NAMES = tuple(l.name for l in LEVELS)
SPECIFICATIONS = {l.index: l for l in LEVELS}


# ────────────────────────────────────────────────────────────────
# Level constructors
# ────────────────────────────────────────────────────────────────
def _alg_at(level: int) -> Alg:
    """Return the algebra descriptor appropriate for `level`."""
    if level == 0:
        return BOOL_ALG
    # build a recursive Alg on top of the previous level
    inner = _alg_at(level - 1)

    def add(a: CD, b: CD) -> CD:
        return a + b
    def sub(a: CD, b: CD) -> CD:
        return a - b
    def mul(a: CD, b: CD) -> CD:
        return a * b
    def neg(a: CD) -> CD:
        return -a
    def conj(a: CD) -> CD:
        return a.conj()
    def is_zero(a: CD) -> bool:
        return a.is_zero()

    return Alg(add=add, sub=sub, mul=mul, neg=neg, conj=conj,
               is_zero=is_zero,
               zero=cd_zero(inner, level - 1),
               one=cd_one(inner, level - 1),
               name=f"cd-L{level}")


# ────────────────────────────────────────────────────────────────
# Per-level modules
# ────────────────────────────────────────────────────────────────
def boolean_level():
    """L0: NAND is the only primitive."""
    return {
        "level": 0,
        "name": "Boolean logic",
        "primitive": NAND,
        "basis": (False, True),
        "algebra": BOOL_ALG,
        "spec": LEVELS[0],
    }


def lambda_level():
    """L1: pairs of Booleans, commutative lost."""
    basis = cd_basis(BOOL_ALG, 1)
    return {
        "level": 1,
        "name": "Lambda calculus",
        "basis": basis,           # [e0, e1]
        "algebra": _alg_at(1),
        "spec": LEVELS[1],
        "note": "e0 = I = True; e1 = the first non-commutative generator",
    }


def combinatory_level():
    basis = cd_basis(BOOL_ALG, 2)
    return {
        "level": 2,
        "name": "Combinatory logic",
        "basis": basis,
        "algebra": _alg_at(2),
        "spec": LEVELS[2],
        "note": "basis[1] ~ K, basis[2] ~ S (as CD 4-vectors)",
    }


def turing_level():
    return {
        "level": 3,
        "name": "Turing machine",
        "basis": cd_basis(BOOL_ALG, 3),
        "algebra": _alg_at(3),
        "spec": LEVELS[3],
        "note": "8 basis elements: q0..q1 x s0..s3 heads",
    }


def pi_level():
    return {
        "level": 4,
        "name": "Pi calculus",
        "basis": cd_basis(BOOL_ALG, 4),
        "algebra": _alg_at(4),
        "spec": LEVELS[4],
        "note": "16 basis elements: send/recv/par/new at two channels",
    }


def interaction_level():
    return {
        "level": 5,
        "name": "Interaction combinators",
        "basis": cd_basis(BOOL_ALG, 5),
        "algebra": _alg_at(5),
        "spec": LEVELS[5],
        "note": "32 basis elements: gamma/delta/epsilon triples",
    }


def ca_level():
    return {
        "level": 6,
        "name": "Cellular automata",
        "basis": cd_basis(BOOL_ALG, 6),
        "algebra": _alg_at(6),
        "spec": LEVELS[6],
        "note": "64 basis elements: 2^3 neighborhoods x 8 cell phases",
    }


def category_level():
    return {
        "level": 7,
        "name": "Category theory",
        "basis": cd_basis(BOOL_ALG, 7),
        "algebra": _alg_at(7),
        "spec": LEVELS[7],
        "note": "128 basis elements: id / compose formalized as products",
    }


def quantum_level():
    return {
        "level": 8,
        "name": "Quantum mechanics",
        "basis": cd_basis(BOOL_ALG, 8),
        "algebra": _alg_at(8),
        "spec": LEVELS[8],
        "note": "256 basis elements: [x, p] is a CD commutator",
    }


def general_level():
    return {
        "level": 9,
        "name": "General computation",
        "basis": cd_basis(BOOL_ALG, 9),
        "algebra": _alg_at(9),
        "spec": LEVELS[9],
        "note": "512 basis elements: F is any CD-linear map",
    }


LEVEL_CONSTRUCTORS: dict[int, Callable[[], dict]] = {
    0: boolean_level,
    1: lambda_level,
    2: combinatory_level,
    3: turing_level,
    4: pi_level,
    5: interaction_level,
    6: ca_level,
    7: category_level,
    8: quantum_level,
    9: general_level,
}


def level_module(index: int) -> dict:
    if index not in LEVEL_CONSTRUCTORS:
        raise KeyError(f"unknown level: {index}")
    return LEVEL_CONSTRUCTORS[index]()


# ────────────────────────────────────────────────────────────────
# Tower
# ────────────────────────────────────────────────────────────────
@dataclass
class Tower:
    """A materialized tower up to `depth`. Each level is a dict."""
    depth: int = 9
    levels: list = field(default_factory=list)

    def build(self) -> Tower:
        self.levels = [level_module(i) for i in range(self.depth + 1)]
        return self

    def summary(self) -> list:
        return [
            {"level": L["level"], "name": L["name"],
             "dim": len(L["basis"]),
             "loses": L["spec"].loses,
             "invariant": L["spec"].invariant,
             "primitives": list(L["spec"].primitives)}
            for L in self.levels
        ]

    def __repr__(self) -> str:
        lines = ["CD tower over NAND:"]
        for L in self.levels:
            lines.append(
                f"  L{L['level']}  dim={len(L['basis']):>4}  "
                f"{L['name']:<24}  loses: {L['spec'].loses}"
            )
        return "\n".join(lines)


def full_tower() -> Tower:
    return Tower(depth=9).build()
