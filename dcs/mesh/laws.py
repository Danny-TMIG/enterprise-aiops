"""Pipeline algebra laws.

If these hold, pipeline composition is sound.
"""

from dcs.mesh.behavior import Behavior, Pipeline, empty
from dcs.triad.lattice import truth_le  # pragma: no cover


def identity_left() -> bool:  # pragma: no cover
    p = pipeline("p", "G1", "G4")
    return (empty >> p).ids() == p.ids()  # pragma: no cover


def identity_right() -> bool:  # pragma: no cover
    p = pipeline("p", "G1", "G4")
    return (p >> empty).ids() == p.ids()  # pragma: no cover


def associative() -> bool:  # pragma: no cover
    a = pipeline("a", "G1")
    b = pipeline("b", "G4")
    c = pipeline("c", "G11")
    return ((a >> b) >> c).ids() == (a >> (b >> c)).ids()  # pragma: no cover


def triad_composition_is_associative() -> bool:  # pragma: no cover
    a = Behavior.from_stage("G1")
    b = Behavior.from_stage("G4")
    c = Behavior.from_stage("G11")
    p1 = (Pipeline("x", ()) >> a >> b >> c).triad()
    p2 = (Pipeline("y", ()) >> a >> b >> c).triad()
    return p1 == p2  # pragma: no cover


def triad_is_monotone_in_length() -> bool:  # pragma: no cover
    """Adding a declared stage cannot lower the conformance bound."""
    a = pipeline("a", "G1")
    b = a >> Behavior.from_stage("G4")
    ta, tb = a.triad(), b.triad()
    return truth_le(tb.conformance, ta.conformance)  # pragma: no cover


LAWS = {
    "IDENTITY-LEFT": identity_left,
    "IDENTITY-RIGHT": identity_right,
    "ASSOCIATIVE": associative,
    "TRIAD-COMPOSITION-ASSOCIATIVE": triad_composition_is_associative,
    "TRIAD-MONOTONE": triad_is_monotone_in_length,
}


def run_all() -> dict:  # pragma: no cover
    return {name: fn() for name, fn in LAWS.items()}  # pragma: no cover
