"""Driver: parallel grids, dynamic difficulty, difference engine."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.engines.kinds import KINDS, SOLVERS
from app.engines.parallel import run_grid, Outcome, Tile
from app.engines.differential import DiffEngine
from app.engines.dynamic import Controller


@dataclass
class Generation:
    index: int
    difficulty: Dict[str, str]
    tiles: List[Tile]
    rate_by_kind: Dict[str, float]
    duration_ms: float

    def to_dict(self):
        return {
            "index": self.index,
            "difficulty": self.difficulty,
            "rate_by_kind": {k: round(v, 4) for k, v in self.rate_by_kind.items()},
            "duration_ms": round(self.duration_ms, 2),
        }


@dataclass
class Driver:
    puzzles_per_tile: int = 4
    generations: int = 4
    seed: int = 0
    high: float = 0.85
    low: float = 0.25
    kinds: Optional[List[str]] = None
    solvers_by_kind: Optional[Dict[str, List[str]]] = None

    def run(self) -> dict:
        kinds = self.kinds or list(KINDS.keys())
        solvers_by_kind = self.solvers_by_kind or {
            k: list(SOLVERS.get(k, {}).keys()) for k in kinds
        }
        ctrl = Controller(high=self.high, low=self.low)
        ctrl.initialise(kinds)
        diff = DiffEngine(solvers_by_kind)
        gens: List[Generation] = []

        for g in range(self.generations):
            t0 = time.time()
            difficulty = ctrl.current()
            outcomes, tiles = run_grid(
                difficulty_by_kind=difficulty,
                puzzles_per_tile=self.puzzles_per_tile,
                seed=self.seed + g * 1000,
                kinds=kinds,
                solvers_by_kind=solvers_by_kind,
            )
            # compute per-kind mean rate
            rate_by_kind: Dict[str, float] = {}
            rate_by_kind_solver: Dict[str, Dict[str, float]] = {}
            for t in tiles:
                rate_by_kind_solver.setdefault(t.kind, {})[t.solver] = t.rate
            for k, rmap in rate_by_kind_solver.items():
                rate_by_kind[k] = (sum(rmap.values()) / len(rmap)) if rmap else 0.0
                diff.push(k, rmap)
            gens.append(Generation(
                index=g, difficulty=dict(difficulty), tiles=tiles,
                rate_by_kind=rate_by_kind,
                duration_ms=(time.time() - t0) * 1000.0,
            ))
            ctrl.step(rate_by_kind)

        return {
            "generations": [g.to_dict() for g in gens],
            "difficulty_history": ctrl.to_dict(),
            "difference": diff.summary(),
            "final_tiles": {f"{t.kind}/{t.solver}": t.to_dict()
                            for t in gens[-1].tiles} if gens else {},
        }
