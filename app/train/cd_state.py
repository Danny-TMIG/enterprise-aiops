"""Cayley-Dickson state: compress a Run into a CD vector.

Every solver at every (kind, difficulty) becomes a coordinate.
The coordinate value is the success rate. The whole grid becomes
one CD element whose level is ceil(log2(n_coords)).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from app.cd_nand.cayley import CD, alg_at, cd_from, cd_zero
from app.train.core import Run


@dataclass
class CDState:
    run_index: int
    coordinates: list[tuple[str, str, str]]
    values: list[float]
    level: int
    cd: CD

    def to_dict(self):
        return {
            "run_index": self.run_index,
            "n_coordinates": len(self.coordinates),
            "level": self.level,
            "coordinates": [f"{k}/{s}/{d}" for k, s, d in self.coordinates],
            "values": [round(v, 4) for v in self.values],
        }


def _value_to_bool(v: float) -> bool:
    return v >= 0.5


def resolve_cd(run: Run) -> CDState:
    tiles = sorted(run.tiles, key=lambda t: (t.kind, t.solver, t.difficulty))
    coords = [(t.kind, t.solver, t.difficulty) for t in tiles]
    values = [t.rate for t in tiles]

    n = len(tiles)
    if n == 0:
        return CDState(run.index, [], [], 0, cd_zero(0))
    level = max(0, int(math.ceil(math.log2(n))))

    # pad to 2^level
    coords_padded = list(coords)
    values_padded = list(values)
    while len(coords_padded) < (1 << level):
        coords_padded.append(("", "", ""))
        values_padded.append(0.0)

    # build a CD element with Boolean thresholds at the leaves
    bits = [_value_to_bool(v) for v in values_padded]
    cd = _bits_to_cd(bits, level)
    return CDState(run.index, coords, values, level, cd)


def _bits_to_cd(bits: list[bool], level: int) -> CD:
    if level == 0:
        return cd_from(bits[0], 0)
    half = 1 << (level - 1)
    hi = _bits_to_cd(bits[:half], level - 1)
    lo = _bits_to_cd(bits[half:], level - 1)
    return CD(hi, lo, level=level, op=alg_at(level))
