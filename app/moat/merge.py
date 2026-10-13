"""Merge operation.

Two ways to merge:

  1.  `merge(scores)` — vertical merge of a subsystem set into a
      single aggregate over the 8 axes.  This is what produces the
      97 / 6 / 16 numbers.

  2.  `merge(a, b)` — horizontal merge of two AxisScores, taking
      the max on each axis and unioning the notes.  This is what
      stitches subsystems into a moat mesh.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from statistics import mean
from typing import Any

from app.moat.axes import AXES, Axis, AxisScore


@dataclass
class MergeEdge:
    src: str
    dst: str
    axis: Axis
    weight: float

    def to_dict(self) -> dict[str, Any]:
        return {"src": self.src, "dst": self.dst,
                "axis": self.axis.value, "weight": self.weight}


@dataclass
class MergeResult:
    scores: list[AxisScore] = field(default_factory=list)
    axes: dict[str, float] = field(default_factory=dict)
    edges: list[MergeEdge] = field(default_factory=list)
    moat: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "subsystems": len(self.scores),
            "axes": self.axes,
            "moat": self.moat,
            "edges": [e.to_dict() for e in self.edges],
        }


def _mean(xs: Iterable[float]) -> float:
    xs = list(xs)
    return mean(xs) if xs else 0.0


def merge(a: AxisScore, b: AxisScore) -> AxisScore:
    """Horizontal merge: take the max on every axis."""
    m = AxisScore(subsystem=f"{a.subsystem}+{b.subsystem}",
                  path=a.path)
    for ax in AXES:
        setattr(m, ax.name.lower(), max(a.get(ax), b.get(ax)))
    m.notes = list(set(a.notes + b.notes))
    return m


def merge_all(scores: list[AxisScore]) -> AxisScore:
    if not scores:
        return AxisScore(subsystem="empty", path="")
    m = scores[0]
    for s in scores[1:]:
        m = merge(m, s)
    return m


def merge_set(scores: list[AxisScore]) -> MergeResult:
    """Vertical merge: aggregate across subsystems, compute the moat.

    The three axes are weighted as in the earlier decomposition:
        E  existence      weight 1.0
        X  reality        weight 3.0   (reality is the real bottleneck)
        V  verification   weight 2.0   (verification is the next bottleneck)

    The other five axes are reported but do not enter the moat
    product; they are the *shape*, not the *substance*.
    """
    n = len(scores)
    if n == 0:
        return MergeResult()

    agg: dict[str, float] = {}
    for ax in AXES:
        agg[ax.value] = round(_mean(s.get(ax) for s in scores), 4)

    E, X, V = agg["exists"], agg["real"], agg["verified"]
    # the moat product over the three weighted axes
    moat = round(E * (X ** 3) * (V ** 2), 6)

    # edges: every subsystem that scores low on X or V becomes a
    # "thin" edge the moat wants to reinforce
    edges: list[MergeEdge] = []
    for s in scores:
        if s.x < 0.5:
            edges.append(MergeEdge(s.subsystem, "REALITY", Axis.X, 1.0 - s.x))
        if s.v < 0.5:
            edges.append(MergeEdge(s.subsystem, "VERIFY", Axis.V, 1.0 - s.v))

    return MergeResult(scores=scores, axes=agg, edges=edges, moat=moat)
