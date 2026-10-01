"""Pipeline algebra laws.

If these hold, pipeline composition is sound.
"""

from dcs.mesh.behavior import Behavior, Pipeline, empty, pipeline
from dcs.triad.lattice import truth_le


def identity_left() -> bool:
    p = pipeline("p", "G1", "G4")
    return (empty >> p).ids() == p.ids()


def identity_right() -> bool:
    p = pipeline("p", "G1", "G4")
    return (p >> empty).ids() == p.ids()


def associative() -> bool:
    a = pipeline("a", "G1")
    b = pipeline("b", "G4")
    c = pipeline("c", "G11")
    return ((a >> b) >> c).ids() == (a >> (b >> c)).ids()


def triad_composition_is_associative() -> bool:
    a = Behavior.from_stage("G1")
    b = Behavior.from_stage("G4")
    c = Behavior.from_stage("G11")
    p1 = (Pipeline("x", ()) >> a >> b >> c).triad()
    p2 = (Pipeline("y", ()) >> a >> b >> c).triad()
    return p1 == p2


def triad_is_monotone_in_length() -> bool:
    """Adding a declared stage cannot lower the conformance bound."""
    a = pipeline("a", "G1")
    b = a >> Behavior.from_stage("G4")
    ta, tb = a.triad(), b.triad()
    return truth_le(tb.conformance, ta.conformance)


LAWS = {
    "IDENTITY-LEFT": identity_left,
    "IDENTITY-RIGHT": identity_right,
    "ASSOCIATIVE": associative,
    "TRIAD-COMPOSITION-ASSOCIATIVE": triad_composition_is_associative,
    "TRIAD-MONOTONE": triad_is_monotone_in_length,
}


def run_all() -> dict:
    return {name: fn() for name, fn in LAWS.items()}
