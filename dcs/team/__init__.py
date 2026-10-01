"""Team roster — deterministic partition of the hat set."""
from __future__ import annotations

from dcs.hats import HATS


def _partition(hats: list[str]) -> dict[str, list[str]]:
    """Split hats into 4 balanced teams. Stable across runs."""
    teams: dict[str, list[str]] = {"alpha": [], "beta": [], "gamma": [], "delta": []}
    for i, h in enumerate(sorted(hats)):
        teams[list(teams)[i % 4]].append(h)
    return teams


ROSTER: dict[str, list[str]] = _partition(list(HATS))
