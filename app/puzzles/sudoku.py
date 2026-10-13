"""Sudoku — 81 vars, 27 all-different constraints (partial)."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.puzzles.grid import Constraint, Grid, Var
from app.puzzles.solver import solve

N = 9
BOX = 3


def _vid(r, c): return f"r{r}c{c}"


def _all_diff_partial(vals):
    seen = set()
    for v in vals:
        if v is None:
            continue
        if v in seen:
            return False
        seen.add(v)
    return True


@dataclass
class SudokuPuzzle:
    grid: Grid
    givens: dict[str, int] = field(default_factory=dict)
    seed: int = 0

    def solve(self, max_nodes=1_000_000):
        return solve(self.grid, max_nodes=max_nodes)

    def to_matrix(self, assignment=None):
        m = [[0]*N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                v = _vid(r, c)
                if assignment is not None and v in assignment:
                    m[r][c] = assignment[v]
                elif v in self.givens:
                    m[r][c] = self.givens[v]
        return m

    def to_str(self, m=None):
        m = m if m is not None else self.to_matrix()
        out = []
        for r in range(N):
            if r and r % BOX == 0:
                out.append("+-------+-------+-------+")
            row = []
            for c in range(N):
                if c and c % BOX == 0:
                    row.append("|")
                row.append(str(m[r][c] if m[r][c] else "."))
            out.append(" ".join(row))
        return "\n".join(out)


def make_sudoku(givens=None, seed=0):
    if givens is None:
        givens = [
            (0,0,5),(0,1,3),(0,4,7),
            (1,0,6),(1,3,1),(1,4,9),(1,5,5),
            (2,1,9),(2,2,8),(2,7,6),
            (3,0,8),(3,4,6),(3,8,3),
            (4,0,4),(4,3,8),(4,5,3),(4,8,1),
            (5,0,7),(5,4,2),(5,8,6),
            (6,1,6),(6,6,2),(6,7,8),
            (7,3,4),(7,4,1),(7,5,9),(7,8,5),
            (8,4,8),(8,7,7),(8,8,9),
        ]
    gmap = {}
    for r, c, v in givens:
        gmap[_vid(r, c)] = v
    grid = Grid(meta={"kind": "sudoku", "seed": seed})
    for r in range(N):
        for c in range(N):
            v = _vid(r, c)
            dom = [gmap[v]] if v in gmap else list(range(1, 10))
            grid.add_var(Var(id=v, domain=dom, coords=[(r, c)],
                             meta={"row": r, "col": c}))

    def mk(scope):
        def check(a, s=scope):
            return _all_diff_partial([a.get(x) for x in s])
        return check

    for r in range(N):
        sc = [_vid(r, c) for c in range(N)]
        grid.add_constraint(Constraint(f"row{r}", sc, mk(sc)))
    for c in range(N):
        sc = [_vid(r, c) for r in range(N)]
        grid.add_constraint(Constraint(f"col{c}", sc, mk(sc)))
    for br in range(BOX):
        for bc in range(BOX):
            sc = [_vid(br*BOX+dr, bc*BOX+dc)
                  for dr in range(BOX) for dc in range(BOX)]
            grid.add_constraint(Constraint(f"box{br}{bc}", sc, mk(sc)))
    return SudokuPuzzle(grid=grid, givens=gmap, seed=seed)


def solve_sudoku(puzzle, max_nodes=1_000_000):
    s = puzzle.solve(max_nodes=max_nodes)
    if not s.complete:
        return {"solved": False, "nodes": s.nodes}
    return {"solved": True, "nodes": s.nodes,
            "str": puzzle.to_str(puzzle.to_matrix(s.assignment))}
