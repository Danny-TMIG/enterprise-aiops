import pytest

from app.puzzles.rubik import MOVES, SOLVED, apply_move, scramble, solve_cube
from app.train.core import TrainConfig, Trainer
from app.train.mesh import criss_cross, pollinate, trans, weave


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
    # Even at n_moves=2 with a deliberately bad seed, guard holds.
    for seed in range(20):
        assert scramble(n_moves=2, seed=seed) != SOLVED


def test_trainer_evolves_config():
    cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                      puzzles_per_tile=1, seed=0)
    tr = Trainer(cfg)
    before = tr.cfg
    tr.step(0)
    after = tr.cfg
    # Config must be replace-able, not the same object.
    assert after is not before


def test_trans_ancestry():
    cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                      puzzles_per_tile=1, seed=0)
    tr = Trainer(cfg)
    r0 = tr.step(0)
    r1 = tr.step(1)
    r2 = tr.step(2)
    out = trans([r0, r1, r2])
    # Each step is derived from the previous: a chain of 3.
    assert out["edges"] == 2
    assert out["transitive_pairs"] == 3
    assert out["reachable"][r0.id] == 2
    assert out["reachable"][r1.id] == 1
    assert out["reachable"][r2.id] == 0


def test_pollinate_reports_stream_diff():
    cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy", "medium"],
                      puzzles_per_tile=2, seed=0)
    tr = Trainer(cfg)
    a = tr.run_once(0)
    b = tr.run_once(1)
    pairs = pollinate(a, b)
    assert isinstance(pairs, list)
    for p in pairs:
        assert set(p) == {"stream", "change", "a", "b", "delta"}
        assert p["change"] in {"added", "removed", "changed"}


def test_evolve_rotates_difficulties():
    cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                      puzzles_per_tile=1, seed=0)
    tr = Trainer(cfg)
    seen = []
    for i in range(4):
        tr.step(i)
        seen.append(tuple(sorted(tr.cfg.difficulties)))
    # At least two distinct difficulty sets must have appeared.
    assert len(set(seen)) >= 2, seen


def test_pollinate_sees_stream_diff_after_rotation():
    cfg = TrainConfig(kinds=["sudoku", "tictactoe"],
                      difficulties=["easy", "medium"],
                      puzzles_per_tile=1, seed=0)
    tr = Trainer(cfg)
    r0 = tr.step(0)
    r1 = tr.step(1)
    r2 = tr.step(2)
    total = len(pollinate(r0, r1)) + len(pollinate(r1, r2))
    assert total > 0, "pollinate returned nothing across rotated configs"


def test_weave_and_criss_cross():
    cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                      puzzles_per_tile=1, seed=0)
    tr = Trainer(cfg)
    a, b = tr.run_once(0), tr.run_once(1)
    w = weave([a, b])
    assert w["runs"] == 2
    cc = criss_cross(a, b)
    assert cc["combined"].startswith("sha256:")
