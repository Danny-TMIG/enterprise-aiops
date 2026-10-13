"""Puzzle kinds and solver strategies.

A Kind knows how to:
  sample(difficulty, seed)  -> puzzle
  verify(puzzle, attempt)   -> bool
  format(puzzle)            -> str     (for display)

A Solver is a named strategy for one kind:
  solve(puzzle, seed)       -> attempt

Kinds and solvers compose into the parallel grid.
"""
from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Kind:
    name: str
    sample: Callable[[str, int], Any]
    verify: Callable[[Any, Any], bool]
    format: Callable[[Any], str]


# ─────────────────────────────────────────────────────────────────
# SUDOKU
# ─────────────────────────────────────────────────────────────────
def _sudoku_sample(difficulty: str, seed: int):
    from app.puzzles.sudoku import make_sudoku
    # just use the built-in medium puzzle for all difficulties;
    # difficulty is unused for sudoku for now
    return make_sudoku(seed=seed)


def _sudoku_verify(puzzle, attempt):
    if attempt is None:
        return False
    m = attempt
    if len(m) != 9 or any(len(row) != 9 for row in m):
        return False
    for r in range(9):
        if sorted(m[r]) != list(range(1, 10)):
            return False
    for c in range(9):
        col = [m[r][c] for r in range(9)]
        if sorted(col) != list(range(1, 10)):
            return False
    for br in range(3):
        for bc in range(3):
            box = [m[br*3+dr][bc*3+dc] for dr in range(3) for dc in range(3)]
            if sorted(box) != list(range(1, 10)):
                return False
    return True


def _sudoku_format(p):
    return "9x9"


def _sudoku_random(puzzle, seed):
    """Fill randomly; will almost always fail."""
    rng = random.Random(seed)
    gmap = dict(puzzle.givens)
    m = [[0]*9 for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = gmap.get(f"r{r}c{c}")
            m[r][c] = v if v else rng.randint(1, 9)
    return m


def _sudoku_greedy(puzzle, seed):
    """Same search as full, but with a tighter node cap so it can
    fail honestly on hard instances."""
    from app.puzzles.solver import solve_fc
    s = solve_fc(puzzle.grid, max_nodes=1_000_000)
    if not s.complete:
        return None
    return puzzle.to_matrix(s.assignment)


def _sudoku_full(puzzle, seed):
    from app.puzzles.solver import solve_fc
    s = solve_fc(puzzle.grid, max_nodes=1_000_000)
    if not s.complete:
        return None
    return puzzle.to_matrix(s.assignment)


# ─────────────────────────────────────────────────────────────────
# CROSSWORD
# ─────────────────────────────────────────────────────────────────
def _cw_sample(difficulty: str, seed: int):
    from app.puzzles.atlas import load_atlas
    from app.puzzles.crossword import make_crossword
    return make_crossword(atlas=load_atlas(), seed=seed)


def _cw_verify(puzzle, attempt):
    if not isinstance(attempt, dict):
        return False
    for slot in puzzle.slots:
        w = attempt.get(slot.id)
        if not w or len(w) != slot.length:
            return False
    # check intersections
    for c in puzzle.grid.constraints:
        if not c.satisfied(attempt):
            return False
    return True


def _cw_format(p):
    return "4x4"


def _cw_random(puzzle, seed):
    rng = random.Random(seed)
    pool = list(puzzle.grid.vars["A1"].domain)
    return {slot.id: rng.choice(pool) for slot in puzzle.slots}


def _cw_greedy(puzzle, seed):
    """Deterministic greedy: pick A1 from the pool, then D1 whose
    first letter matches A1[0], then D2 whose first letter matches
    A1[3], then A2 whose first letter matches D1[3] and last
    letter matches D2[3]. Returns None if no path is possible."""
    pool = sorted(set(puzzle.grid.vars["A1"].domain))
    for a1 in pool:
        for d1 in pool:
            if d1 == a1 or d1[0] != a1[0]:
                continue
            for d2 in pool:
                if d2 in (a1, d1) or d2[0] != a1[3]:
                    continue
                for a2 in pool:
                    if a2 in (a1, d1, d2):
                        continue
                    if a2[0] == d1[3] and a2[3] == d2[3]:
                        return {"A1": a1, "D1": d1, "D2": d2, "A2": a2}
    return None


def _cw_full(puzzle, seed):
    """Crossword needs the generic backtracker, not forward
    checking. Forward checking removes an entire word from a
    peer's domain, but crossword constraints only require
    equality at specific letter positions — many words that
    share the intersection letters are valid. Pruning the whole
    word discards them. solve() consults Constraint.satisfied
    per candidate, which is what crossword needs."""
    from app.puzzles.solver import solve
    s = solve(puzzle.grid, max_nodes=100_000)
    if not s.complete:
        return None
    return s.assignment


# ─────────────────────────────────────────────────────────────────
# RUBIK 2x2
# ─────────────────────────────────────────────────────────────────
def _rubik_sample(difficulty: str, seed: int):
    from app.puzzles.rubik import scramble
    depth = {"easy": 4, "medium": 6, "hard": 9}.get(difficulty, 6)
    return scramble(n_moves=depth, seed=seed)


def _rubik_verify(puzzle, attempt):
    from app.puzzles.rubik import SOLVED
    if attempt is None:
        return False
    return attempt == SOLVED


def _rubik_format(p):
    return "8-corner"


def _rubik_random(puzzle, seed):
    """Random walk; almost certainly fails."""
    from app.puzzles.rubik import MOVES, apply_move
    rng = random.Random(seed)
    s = puzzle
    for _ in range(20):
        m = rng.choice(list(MOVES.keys()))
        s = apply_move(MOVES[m], s)
    return s


def _rubik_bfs(puzzle, seed):
    from app.puzzles.rubik import solve_cube
    r = solve_cube(puzzle)
    if not r["solved"]:
        return None
    from app.puzzles.rubik import MOVES, apply_move
    s = puzzle
    for m in r["solution"]:
        s = apply_move(MOVES[m], s)
    return s


# ─────────────────────────────────────────────────────────────────
# TIC-TAC-TOE
# ─────────────────────────────────────────────────────────────────
def _ttt_sample(difficulty: str, seed: int):
    """Sample a random mid-game board with X to move."""
    from app.puzzles.tictactoe import EMPTY, O, TTState, X
    rng = random.Random(seed)
    b = [EMPTY]*9
    n = rng.randint(0, 6)
    to_move = X
    for _ in range(n):
        empty = [i for i, v in enumerate(b) if v == EMPTY]
        if not empty:
            break
        i = rng.choice(empty)
        b[i] = to_move
        to_move = O if to_move == X else X
    return TTState(board=tuple(b), to_move=to_move)


def _ttt_verify(puzzle, attempt):
    """Attempt is a move index. Verify it is not losing."""
    from app.puzzles.tictactoe import EMPTY, TicTacToe
    if attempt is None or not (0 <= attempt < 9):
        return False
    if puzzle.board[attempt] != EMPTY:
        return False
    t = TicTacToe()
    state = puzzle
    new_state = t.apply(state, attempt)
    if t.is_terminal(new_state):
        w = new_state.winner()
        return w == state.to_move   # win is fine, draw is fine
    # ensure opponent cannot immediately win on next move
    for opp_move in t.actions(new_state):
        opp_state = t.apply(new_state, opp_move)
        if t.is_terminal(opp_state) and opp_state.winner() is not None:
            return False
    return True


def _ttt_format(p):
    return "board"


def _ttt_random(puzzle, seed):
    from app.puzzles.tictactoe import EMPTY
    rng = random.Random(seed)
    empty = [i for i, v in enumerate(puzzle.board) if v == EMPTY]
    return rng.choice(empty) if empty else None


def _ttt_center(puzzle, seed):
    """Prefer center, then corners, then edges."""
    from app.puzzles.tictactoe import EMPTY
    empty = [i for i, v in enumerate(puzzle.board) if v == EMPTY]
    if not empty:
        return None
    order = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    for i in order:
        if i in empty:
            return i
    return empty[0]


def _ttt_minimax(puzzle, seed):
    from app.puzzles.tictactoe import TicTacToe
    from app.puzzles.tree import alpha_beta

    class _Wrap:
        def __init__(self, state):
            self.initial = lambda: state
            self.actions = lambda s: [i for i, v in enumerate(s.board) if v == 0]
            self.apply = lambda s, a: TicTacToe().apply(s, a)
            self.is_terminal = lambda s: TicTacToe().is_terminal(s)
            self.reward = lambda s, p: TicTacToe().reward(s, p)
            self.heuristic = lambda s, p: 0.0
    w = _Wrap(puzzle)
    r = alpha_beta(w, max_depth=9)
    return r.best_action


# ─────────────────────────────────────────────────────────────────
# GRIDWORLD
# ─────────────────────────────────────────────────────────────────
def _gw_sample(difficulty: str, seed: int):
    from app.puzzles.gridworld import Gridworld
    return Gridworld()


def _gw_verify(puzzle, attempt):
    """Attempt is a list of actions. Verify the path reaches goal."""
    if not attempt:
        return False
    g = puzzle
    s = g.initial()
    for a in attempt:
        if g.is_terminal(s):
            break
        try:
            s = g.apply(s, a)
        except Exception:
            return False
    return g.is_terminal(s)


def _gw_format(p):
    return "9x9 grid"


def _gw_random(puzzle, seed):
    g = puzzle
    rng = random.Random(seed)
    s = g.initial()
    path = []
    for _ in range(50):
        if g.is_terminal(s):
            return path
        acts = g.actions(s)
        if not acts:
            break
        a = rng.choice(acts)
        path.append(a)
        s = g.apply(s, a)
    return path


def _gw_bfs(puzzle, seed):
    from app.puzzles.tree import bfs
    g = puzzle
    r = bfs(g, max_nodes=10_000)
    return list(r.path) if r.found else None


# ─────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────
KINDS: dict[str, Kind] = {
    "sudoku":    Kind("sudoku",    _sudoku_sample, _sudoku_verify, _sudoku_format),
    "crossword": Kind("crossword", _cw_sample,     _cw_verify,     _cw_format),
    "rubik":     Kind("rubik",     _rubik_sample,  _rubik_verify,  _rubik_format),
    "tictactoe": Kind("tictactoe", _ttt_sample,    _ttt_verify,    _ttt_format),
    "gridworld": Kind("gridworld", _gw_sample,     _gw_verify,     _gw_format),
}

SOLVERS: dict[str, dict[str, Callable]] = {
    "sudoku":    {"random": _sudoku_random, "greedy": _sudoku_greedy, "full": _sudoku_full},
    "crossword": {"random": _cw_random,     "greedy": _cw_greedy,     "full": _cw_full},
    "rubik":     {"random": _rubik_random,  "bfs":    _rubik_bfs},
    "tictactoe": {"random": _ttt_random,    "center": _ttt_center,    "minimax": _ttt_minimax},
    "gridworld": {"random": _gw_random,     "bfs":    _gw_bfs},
}


def list_kinds() -> list:
    return sorted(KINDS.keys())


def list_solvers(kind: str) -> list:
    return sorted(SOLVERS.get(kind, {}).keys())

# Fibonacci-spaced difficulty radii for puzzle generation.
# Instead of {"easy": 4, "medium": 6, "hard": 9}, use Fibonacci
# ratios so the perceptual distance between levels is uniform.
FIB_LEVELS = {"easy": 5, "medium": 8, "hard": 13}

_ORIG_RUBIK_SAMPLE = _rubik_sample
def _rubik_sample(puzzle_or_diff, seed):
    # accept either the old difficulty name or the raw integer depth
    if isinstance(puzzle_or_diff, str) and puzzle_or_diff in FIB_LEVELS:
        depth = FIB_LEVELS[puzzle_or_diff]
    else:
        depth = int(puzzle_or_diff) if not isinstance(puzzle_or_diff, str) else 6
    from app.puzzles.rubik import scramble
    return scramble(n_moves=depth, seed=seed)
