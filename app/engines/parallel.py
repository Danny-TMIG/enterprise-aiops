"""Parallel grid runner.

Runs (kind, solver, puzzle) triples concurrently in a thread pool.
For CPU-bound solver work, swap ThreadPoolExecutor for
ProcessPoolExecutor; the interface is identical.
"""
from __future__ import annotations

import concurrent.futures as cf
import time
from dataclasses import dataclass

from app.engines.kinds import KINDS, SOLVERS

USE_PROCESSES = True


@dataclass
class Outcome:
    kind: str
    solver: str
    puzzle_id: int
    difficulty: str
    passed: bool
    duration_ms: float
    error: str = ""

    def to_dict(self):
        return {
            "kind": self.kind, "solver": self.solver,
            "puzzle_id": self.puzzle_id, "difficulty": self.difficulty,
            "passed": self.passed,
            "duration_ms": round(self.duration_ms, 2),
            "error": self.error,
        }


@dataclass
class Tile:
    """One (kind, solver) cell of the grid at one generation."""
    kind: str
    solver: str
    trials: int
    passes: int
    duration_ms: float

    @property
    def rate(self) -> float:
        return self.passes / self.trials if self.trials else 0.0

    def to_dict(self):
        return {"kind": self.kind, "solver": self.solver,
                "trials": self.trials, "passes": self.passes,
                "rate": round(self.rate, 4),
                "duration_ms": round(self.duration_ms, 2)}


def _run_one(kind_name: str, solver_name: str, difficulty: str,
             seed: int, puzzle_id: int) -> Outcome:
    t0 = time.time()
    try:
        k = KINDS[kind_name]
        s = SOLVERS[kind_name][solver_name]
        puzzle = k.sample(difficulty, seed)
        attempt = s(puzzle, seed)
        ok = k.verify(puzzle, attempt)
        return Outcome(kind_name, solver_name, puzzle_id, difficulty,
                       bool(ok), (time.time() - t0) * 1000.0)
    except Exception as e:
        return Outcome(kind_name, solver_name, puzzle_id, difficulty,
                       False, (time.time() - t0) * 1000.0,
                       f"{type(e).__name__}: {e}")


def run_grid(difficulty_by_kind: dict[str, str],
             puzzles_per_tile: int = 4,
             seed: int = 0,
             max_workers: int | None = None,
             kinds: list[str] | None = None,
             solvers_by_kind: dict[str, list[str]] | None = None
             ) -> tuple[list[Outcome], list[Tile]]:
    """Run every (kind, solver, puzzle) concurrently.

    Returns (outcomes, tiles).
    """
    kinds = kinds or list(KINDS.keys())
    futures: list[tuple[cf.Future, str, str]] = []
    outcomes: list[Outcome] = []

    if USE_PROCESSES:
        import multiprocessing as mp
        ctx = mp.get_context("fork")
        pool = cf.ProcessPoolExecutor(max_workers=max_workers, mp_context=ctx)
    else:
        pool = cf.ThreadPoolExecutor(max_workers=max_workers)
    with pool:
        for kind in kinds:
            difficulty = difficulty_by_kind.get(kind, "medium")
            solver_names = (solvers_by_kind or {}).get(kind)
            if solver_names is None:
                solver_names = list(SOLVERS.get(kind, {}).keys())
            for solver in solver_names:
                for j in range(puzzles_per_tile):
                    fut = pool.submit(_run_one, kind, solver, difficulty,
                                      seed + j, j)
                    futures.append((fut, kind, solver))
        for fut, kind, solver in futures:
            try:
                outcomes.append(fut.result())
            except Exception as e:
                outcomes.append(Outcome(kind, solver, -1, "?", False,
                                        0.0, f"{type(e).__name__}: {e}"))

    # aggregate into tiles
    tiles: dict[tuple[str, str], Tile] = {}
    for o in outcomes:
        key = (o.kind, o.solver)
        t = tiles.get(key)
        if t is None:
            t = Tile(kind=o.kind, solver=o.solver, trials=0, passes=0,
                     duration_ms=0.0)
            tiles[key] = t
        t.trials += 1
        t.passes += int(o.passed)
        t.duration_ms += o.duration_ms

    return outcomes, list(tiles.values())
