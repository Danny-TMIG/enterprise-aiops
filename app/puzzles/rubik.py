"""Rubik's cube (2x2). Moves are generated, scramble rejects canceling sequences."""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from app.puzzles.tree import DecisionTree

SOLVED: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7)

# Corner permutation for a single clockwise face turn (8 corners, index = position).
_BASE = {
    "U": (1, 2, 3, 0, 4, 5, 6, 7),
    "R": (4, 1, 2, 0, 7, 5, 6, 3),
    "F": (1, 5, 2, 3, 0, 4, 6, 7),
}


def _inverse(sigma: tuple[int, ...]) -> tuple[int, ...]:
    inv = [0] * len(sigma)
    for i, s in enumerate(sigma):
        inv[s] = i
    return tuple(inv)


def _compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(b[a[i]] for i in range(8))


# Moves generated from faces, not hand-written.
MOVES: dict[str, tuple[int, ...]] = {}
for _f, _v in _BASE.items():
    MOVES[_f] = _v
    MOVES[_f + "'"] = _inverse(_v)
    MOVES[_f + "2"] = _compose(_v, _v)

_FACES = tuple(_BASE.keys())
_SUFFIXES = ("", "'", "2")


def _same_face(m1: str, m2: str) -> bool:
    return m1.rstrip("'2") == m2.rstrip("'2")


def apply_move(sigma: tuple[int, ...], state: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(state[sigma[i]] for i in range(8))


@lru_cache(maxsize=1)
def _distance_table():
    dist: dict[tuple[int, ...], int] = {SOLVED: 0}
    parent: dict[tuple[int, ...], tuple[tuple[int, ...], str]] = {}
    q = deque([SOLVED])
    while q:
        s = q.popleft()
        d = dist[s]
        for name, sigma in MOVES.items():
            ns = apply_move(sigma, s)
            if ns not in dist:
                dist[ns] = d + 1
                parent[ns] = (s, name)
                q.append(ns)
    return dist, parent


def scramble(n_moves: int = 11, seed: int = 0) -> tuple[int, ...]:
    """Return a state reachable in exactly `n_moves` non-canceling moves.

    Guarantees: no two consecutive moves share a face, and the final state
    is not SOLVED. A retry loop handles the pathological
    case where a longer sequence happens to compose to identity.
    """
    rng = random.Random(seed)
    for _ in range(128):
        s = SOLVED
        prev = None
        for _ in range(n_moves):
            choices = [f + suf for f, suf in product(_FACES, _SUFFIXES)
                       if prev is None or not _same_face(f, prev)]
            m = rng.choice(choices)
            s = apply_move(MOVES[m], s)
            prev = m
        if s != SOLVED:
            return s
    raise ValueError(
        f"scramble could not produce non-SOLVED state in 128 tries "
        f"(n_moves={n_moves}, seed={seed})"
    )


def solve_cube(state: tuple[int, ...]) -> dict:
    """BFS parent chain, emitting inverse moves (walk order = forward order)."""
    dist, parent = _distance_table()
    if state not in dist:
        return {"solved": False, "nodes": 0, "scramble": state,
                "note": "state not reachable"}

    path: list[str] = []
    cur = state
    while cur != SOLVED:
        prev, move = parent[cur]
        # parent[cur] = (prev, move) with apply(move, prev) == cur,
        # so stepping cur -> prev requires the inverse.
        if move.endswith("'"):
            path.append(move[:-1])
        elif move.endswith("2"):
            path.append(move)      # 180-degree turns are self-inverse
        else:
            path.append(move + "'")
        cur = prev

    return {
        "solved": True,
        "nodes": dist[state],
        "scramble": state,
        "solution": path,
        "solution_len": len(path),
        "reachable_states": len(dist),
    }


@dataclass
class RubikCube(DecisionTree):
    goal: tuple[int, ...] = SOLVED

    def initial(self):
        return self.goal

    def actions(self, s):
        return list(MOVES.keys())

    def apply(self, s, a):
        return apply_move(MOVES[a], s)

    def is_terminal(self, s):
        return s == self.goal

    def reward(self, s, player):
        return 1.0 if s == self.goal else 0.0

    def heuristic(self, s, player):
        dist, _ = _distance_table()
        return float(dist.get(s, 100))
