"""Behavior atoms and Pipeline algebra.

A Behavior is a named stage from one of the six taxonomies. A Pipeline
is a composition of Behaviors. Its Triad is the axis-wise fold of the
Triads of its stages. Composition is associative with an identity, so
pipelines form a monoid over the same bilattice used by TRIAD.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from dcs.mesh.taxonomy import stage as _stage
from dcs.triad import (
    PASS,
    Kernel,
    Receipt,
    Triad,
)
from dcs.triad.axes import coordination as D
from dcs.triad.lattice import join_know, meet_truth


def _fold(states: Iterable, op, empty):
    it = iter(states)
    try:
        acc = next(it)
    except StopIteration:
        return empty
    for s in it:
        acc = op(acc, s)
    return acc


@dataclass(frozen=True)
class Behavior:
    id: str
    family: str
    title: str
    ops: tuple[str, ...]
    axis: str

    @classmethod
    def from_stage(cls, sid: str) -> Behavior:
        s = _stage(sid)
        return cls(
            id=s["id"], family=s["family"], title=s["title"], ops=tuple(s["ops"]), axis=s["axis"]
        )

    def triad(self) -> Triad:
        """A declared behavior passes all three axes by construction."""
        return Triad(PASS, PASS, PASS)

    def describe(self) -> dict:
        return {
            "id": self.id,
            "family": self.family,
            "title": self.title,
            "axis": self.axis,
            "ops": list(self.ops),
        }


@dataclass(frozen=True)
class Pipeline:
    name: str
    stages: tuple[Behavior, ...]

    # --- composition (monoid) ---

    def __rshift__(self, other) -> Pipeline:
        if isinstance(other, Behavior):
            return Pipeline(f"{self.name}>>{other.id}", self.stages + (other,))
        if isinstance(other, Pipeline):
            return Pipeline(f"{self.name}>>{other.name}", self.stages + other.stages)
        raise TypeError(f"cannot compose with {type(other).__name__}")

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):
        return iter(self.stages)

    def ids(self) -> tuple[str, ...]:
        return tuple(s.id for s in self.stages)

    # --- TRIAD integration ---

    def triad(self) -> Triad:
        """Compose stage triads pointwise across the bilattice.

        conformance: meet_truth — every stage must conform.
        coherence:   join_know  — every stage sees the same world.
        coordination: D.merge   — union of stage coordination states.
        """
        if not self.stages:
            return Triad(PASS, PASS, PASS)
        cs = [s.triad().conformance for s in self.stages]
        hs = [s.triad().coherence for s in self.stages]
        ds = [s.triad().coordination for s in self.stages]
        return Triad(_fold(cs, meet_truth, PASS), _fold(hs, join_know, PASS), D.merge(ds))

    def verify(self, *, kernel: Kernel | None = None) -> tuple[Triad, Receipt]:
        k = kernel or Kernel()
        t = self.triad()
        deriv = [{"stage": s.id, "family": s.family, "axis": s.axis} for s in self.stages]
        return t, k.receipt(t, derivation=deriv)

    def contract(self) -> dict:
        """The pipeline's declared interface: stages, axes, ops count."""
        return {
            "name": self.name,
            "length": len(self.stages),
            "stages": [s.describe() for s in self.stages],
            "axes": {
                a: sum(1 for s in self.stages if s.axis in (a, "all"))
                for a in ("conformance", "coherence", "coordination")
            },
        }


empty = Pipeline("∅", ())


def pipeline(name: str, *stage_ids: str) -> Pipeline:
    p = Pipeline(name, ())
    for sid in stage_ids:
        p = p >> Behavior.from_stage(sid)
    return p
