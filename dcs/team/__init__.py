"""Team roster — deterministic partition of the hat set."""

from __future__ import annotations  # pragma: no cover

from dcs.hats import HATS  # pragma: no cover


def _partition(hats: list[str]) -> dict[str, list[str]]:  # pragma: no cover
    """Split hats into 4 balanced teams. Stable across runs."""
    teams: dict[str, list[str]] = {"alpha": [], "beta": [], "gamma": [], "delta": []}
    for i, h in enumerate(sorted(hats)):
        teams[list(teams)[i % 4]].append(h)
    return teams  # pragma: no cover


ROSTER: dict[str, list[str]] = _partition(list(HATS))
