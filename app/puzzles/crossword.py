"""Crossword as a Grid, built from a valid placement.

We search for a 4x4 arrangement of four 4-letter atlas words that
satisfy the intersection constraints, then present that placement
as the puzzle. This guarantees the puzzle is solvable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.puzzles.atlas import CATEGORIES, Atlas, load_atlas
from app.puzzles.grid import Constraint, Grid, Var
from app.puzzles.solver import solve


@dataclass
class Slot:
    id: str
    row: int
    col: int
    direction: str
    length: int
    cells: list[tuple[int, int]]
    clue_category: str = "Semantics"
    clue: str = ""


# Layout (4x4 with 4 slots, 4 intersections):
#
#   A B C D     slot A1 across row 0  = A B C D
#   E . . F     slot D1 down   col 0  = A E G I
#   G . . H     slot D2 down   col 3  = D F H L
#   I J K L     slot A2 across row 3  = I J K L
#
# Constraints (letter matches at intersections):
#   A1[0] == D1[0]      A1[3] == D2[0]
#   A2[0] == D1[3]      A2[3] == D2[3]

_ROW0 = [(0, 0), (0, 1), (0, 2), (0, 3)]
_ROW3 = [(3, 0), (3, 1), (3, 2), (3, 3)]
_COL0 = [(0, 0), (1, 0), (2, 0), (3, 0)]
_COL3 = [(0, 3), (1, 3), (2, 3), (3, 3)]


def _fits(a1: str, d1: str, d2: str, a2: str) -> bool:
    return (a1[0] == d1[0]
            and a1[3] == d2[0]
            and a2[0] == d1[3]
            and a2[3] == d2[3])


def _find_placement(pool: list[str], seed: int = 0
                    ) -> tuple[str, str, str, str] | None:
    """Return (a1, d1, d2, a2) satisfying the layout, or None."""
    # dedupe and keep order deterministic
    words = sorted(set(pool))
    for a1 in words:
        # d1 starts with a1[0], d2 starts with a1[3]
        d1_cands = [w for w in words if w != a1 and w[0] == a1[0]]
        d2_cands = [w for w in words if w != a1 and w[0] == a1[3]]
        for d1 in d1_cands:
            for d2 in d2_cands:
                if d1 == d2:
                    continue
                # a2 starts with d1[3], ends with d2[3]
                a2_cands = [w for w in words
                            if w != a1 and w != d1 and w != d2
                            and w[0] == d1[3] and w[3] == d2[3]]
                for a2 in a2_cands:
                    return (a1, d1, d2, a2)
    return None


def make_crossword(atlas: Atlas | None = None,
                   seed: int = 0) -> CrosswordPuzzle:
    a = atlas or load_atlas()
    pool = a.by_length(4)
    if len(pool) < 4:
        raise ValueError(
            f"atlas needs at least 4 four-letter words (found {len(pool)})")

    placement = _find_placement(pool, seed=seed)
    if placement is None:
        raise ValueError(
            "no valid 4x4 crossword placement exists with the current "
            "atlas pool; try load_atlas() with a larger lexicon")

    a1, d1, d2, a2 = placement

    grid = Grid(meta={"kind": "crossword", "size": 4, "seed": seed})
    slots: list[Slot] = [
        Slot("A1", 0, 0, "A", 4, _ROW0, CATEGORIES[0],
             f"4-letter term in {CATEGORIES[0]}"),
        Slot("D1", 0, 0, "D", 4, _COL0, CATEGORIES[1],
             f"4-letter term in {CATEGORIES[1]}"),
        Slot("D2", 0, 3, "D", 4, _COL3, CATEGORIES[2],
             f"4-letter term in {CATEGORIES[2]}"),
        Slot("A2", 3, 0, "A", 4, _ROW3, CATEGORIES[3],
             f"4-letter term in {CATEGORIES[3]}"),
    ]

    truth = {"A1": a1, "D1": d1, "D2": d2, "A2": a2}

    for slot in slots:
        grid.add_var(Var(
            id=slot.id,
            domain=list(pool),
            coords=slot.cells,
            meta={"direction": slot.direction, "row": slot.row,
                  "col": slot.col, "length": slot.length,
                  "clue_category": slot.clue_category, "clue": slot.clue},
        ))

    def mk_check(s1, i1, s2, i2):
        def check(a):
            w1 = a.get(s1); w2 = a.get(s2)
            if w1 is None or w2 is None:
                return True
            return w1[i1] == w2[i2]
        return check

    pairs = [
        ("A1", 0, "D1", 0),
        ("A1", 3, "D2", 0),
        ("A2", 0, "D1", 3),
        ("A2", 3, "D2", 3),
    ]
    for k, (s1, i1, s2, i2) in enumerate(pairs):
        grid.add_constraint(Constraint(
            id=f"x{k}", scope=[s1, s2],
            check=mk_check(s1, i1, s2, i2)))

    return CrosswordPuzzle(grid=grid, slots=slots, seed=seed,
                           pool_size=len(pool), truth=truth)


@dataclass
class CrosswordPuzzle:
    grid: Grid
    slots: list[Slot]
    seed: int = 0
    pool_size: int = 0
    truth: dict[str, str] = field(default_factory=dict)

    def to_matrix(self, assignment: dict[str, str] | None = None
                  ) -> list[list[str]]:
        m = [["." for _ in range(4)] for _ in range(4)]
        if assignment is None:
            return m
        for slot in self.slots:
            word = assignment.get(slot.id)
            if word is None:
                continue
            for i, (r, c) in enumerate(slot.cells):
                m[r][c] = word[i]
        return m

    def to_str(self, m=None) -> str:
        m = m if m is not None else self.to_matrix()
        return "\n".join(" ".join(row) for row in m)

    def clue_list(self) -> list[dict]:
        return [{"slot": s.id, "direction": s.direction,
                 "row": s.row, "col": s.col,
                 "category": s.clue_category, "clue": s.clue}
                for s in self.slots]


def solve_crossword(puzzle: CrosswordPuzzle,
                    max_nodes: int = 1_000_000) -> dict:
    s = solve(puzzle.grid, max_nodes=max_nodes)
    if not s.complete:
        return {"solved": False, "nodes": s.nodes,
                "partial": s.assignment}
    return {
        "solved": True,
        "nodes": s.nodes,
        "assignment": s.assignment,
        "str": puzzle.to_str(puzzle.to_matrix(s.assignment)),
        "clues": puzzle.clue_list(),
    }
