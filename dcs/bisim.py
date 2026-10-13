"""Bisimulation over labeled transition systems.

An LTS is a dict: state -> list of (label, next_state). Two states are
bisimilar if every transition from one is matched by a same-label
transition from the other to a bisimilar state, and vice versa. That is
the coinductive definition; the implementation is partition refinement.
"""
from __future__ import annotations

from typing import Hashable

Label = Hashable
State = Hashable
LTS = dict[State, list[tuple[Label, State]]]


def _signature(
    lts: LTS, s: State, partition: dict[State, int]
) -> frozenset[tuple[Label, int]]:
    return frozenset(
        (label, partition.get(nxt, -1))
        for label, nxt in lts.get(s, [])
    )


def _refine(lts: LTS) -> dict[State, int]:
    states = list(lts)
    partition: dict[State, int] = {s: 0 for s in states}
    while True:
        sigs = {s: _signature(lts, s, partition) for s in states}
        classes: dict[frozenset, int] = {}
        new_partition: dict[State, int] = {}
        for s in states:
            sig = sigs[s]
            if sig not in classes:
                classes[sig] = len(classes)
            new_partition[s] = classes[sig]
        if new_partition == partition:
            return partition
        partition = new_partition


def bisimilar(lts: LTS, a: State, b: State) -> bool:
    """True if a and b are bisimilar in lts."""
    if a not in lts or b not in lts:
        return False
    return _refine(lts)[a] == _refine(lts)[b]


def equivalence_classes(lts: LTS) -> dict[State, int]:
    """Final partition: state -> class id."""
    return _refine(lts)
