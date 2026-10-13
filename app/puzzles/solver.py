"""Backtracking solver with MRV and forward checking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.puzzles.grid import Grid, VarId


@dataclass
class Solution:
    assignment: dict[VarId, Any]
    nodes: int
    complete: bool
    trace: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"assignment": dict(self.assignment),
                "nodes": self.nodes, "complete": self.complete}


def _mrv(grid, assignment):
    best_id = None
    best = None
    for vid, v in grid.vars.items():
        if vid in assignment:
            continue
        n = len(v.domain)
        if best is None or n < best:
            best = n
            best_id = vid
    return best_id


def _consistent(grid, assignment):
    for c in grid.constraints:
        if not c.satisfied(assignment):
            return False
    return True


def solve(grid: Grid, max_nodes: int = 1_000_000) -> Solution:
    assignment = {}
    nodes = [0]

    def bt():
        if len(assignment) == len(grid.vars):
            return True
        vid = _mrv(grid, assignment)
        if vid is None:
            return True
        var = grid.vars[vid]
        for value in var.domain:
            assignment[vid] = value
            nodes[0] += 1
            if nodes[0] > max_nodes:
                del assignment[vid]
                return False
            if _consistent(grid, assignment):
                if bt():
                    return True
            del assignment[vid]
        return False

    ok = bt()
    return Solution(assignment=dict(assignment), nodes=nodes[0], complete=ok)

def solve_fc(grid: Grid, max_nodes: int = 1_000_000) -> Solution:
    """Backtracking with forward checking.

    When a variable is assigned, its value is removed from the
    domain of every peer that shares a constraint with it. On
    backtrack, the peer domains are restored. This prunes the
    search tree by orders of magnitude compared to solve() for
    dense constraint problems like sudoku.

    Node counts are only comparable across runs of this function,
    not with solve().
    """
    domains = {vid: set(v.domain) for vid, v in grid.vars.items()}
    neighbors = {vid: set() for vid in grid.vars}
    for c in grid.constraints:
        scope = set(c.scope)
        for v in c.scope:
            neighbors[v].update(scope - {v})

    assignment: dict[VarId, Any] = {}
    nodes = [0]

    def pick_mrv():
        best_id = None
        best = None
        for v in grid.vars:
            if v in assignment:
                continue
            n = len(domains[v])
            if best is None or n < best:
                best = n
                best_id = v
        return best_id, (best if best is not None else 0)

    def bt():
        if len(assignment) == len(grid.vars):
            return True
        vid, nd = pick_mrv()
        if vid is None:
            return True
        if nd == 0:
            return False

        # snapshot peers' domains before trying values
        peer_snap = {p: set(domains[p]) for p in neighbors[vid]}

        for value in list(domains[vid]):
            nodes[0] += 1
            if nodes[0] > max_nodes:
                return False
            assignment[vid] = value
            ok = True
            for peer in neighbors[vid]:
                if peer in assignment:
                    if assignment[peer] == value:
                        ok = False
                        break
                    continue
                domains[peer].discard(value)
                if not domains[peer]:
                    ok = False
                    break
            if ok and bt():
                return True
            del assignment[vid]
            for p, s in peer_snap.items():
                domains[p] = set(s)
        return False

    ok = bt()
    return Solution(assignment=dict(assignment), nodes=nodes[0], complete=ok)
