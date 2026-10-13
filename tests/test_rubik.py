"""Rubik-specific tests, runnable in isolation: `pytest tests/test_rubik.py`."""
import pytest

from app.puzzles.rubik import (
    MOVES,
    SOLVED,
    RubikCube,
    apply_move,
    scramble,
    solve_cube,
)


@pytest.mark.parametrize("depth", [2, 4, 6, 8, 10, 11])
def test_scramble_never_solved(depth):
    assert scramble(n_moves=depth, seed=42) != SOLVED


@pytest.mark.parametrize("depth", [2, 4, 6, 8, 10, 11])
def test_solve_cube_roundtrip(depth):
    s = scramble(n_moves=depth, seed=42)
    r = solve_cube(s)
    assert r["solved"]
    cur = s
    for m in r["solution"]:
        cur = apply_move(MOVES[m], cur)
    assert cur == SOLVED


def test_scramble_rejects_cancel():
    for seed in range(20):
        assert scramble(n_moves=2, seed=seed) != SOLVED


def test_heuristic_is_zero_at_goal():
    cube = RubikCube()
    assert cube.heuristic(SOLVED, player=0) == 0.0


def test_actions_are_nonempty():
    cube = RubikCube()
    assert len(cube.actions(SOLVED)) == len(MOVES)
