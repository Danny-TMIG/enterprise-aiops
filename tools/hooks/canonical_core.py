"""Training core. Canonical — do not edit in place; edit here and run tools/hooks/sync.sh."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field, replace

from app.engines.kinds import KINDS, SOLVERS


def _h(*parts) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update(str(p).encode()); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()[:16]


@dataclass
class TrainConfig:
    kinds: list[str] = field(default_factory=lambda: sorted(KINDS.keys()))
    difficulties: list[str] = field(default_factory=lambda: ["easy", "medium", "hard"])
    puzzles_per_tile: int = 4
    seed: int = 0
    max_workers: int | None = None


@dataclass
class TrainOutcome:
    kind: str
    solver: str
    difficulty: str
    puzzle_id: int
    passed: bool
    duration_ms: float
    digest: str

    def to_dict(self):
        return {"kind": self.kind, "solver": self.solver,
                "difficulty": self.difficulty, "puzzle_id": self.puzzle_id,
                "passed": self.passed,
                "duration_ms": round(self.duration_ms, 2),
                "digest": self.digest}


@dataclass
class TrainTile:
    kind: str
    solver: str
    difficulty: str
    trials: int
    passes: int
    duration_ms: float = 0.0

    @property
    def rate(self) -> float:
        return self.passes / self.trials if self.trials else 0.0

    @property
    def key(self) -> str:
        return f"{self.kind}/{self.solver}/{self.difficulty}"

    def to_dict(self):
        return {"kind": self.kind, "solver": self.solver,
                "difficulty": self.difficulty, "trials": self.trials,
                "passes": self.passes, "rate": round(self.rate, 4),
                "duration_ms": round(self.duration_ms, 2)}


@dataclass
class Run:
    index: int
    tiles: list[TrainTile]
    outcomes: list[TrainOutcome]
    duration_ms: float
    digest: str
    parent_id: str | None = None

    @property
    def id(self) -> str:
        return self.digest

    @property
    def rates(self) -> dict[str, float]:
        return {t.key: t.rate for t in self.tiles}

    def to_dict(self):
        return {"index": self.index, "id": self.id,
                "parent_id": self.parent_id, "digest": self.digest,
                "duration_ms": round(self.duration_ms, 2),
                "tiles": [t.to_dict() for t in self.tiles],
                "outcomes": [o.to_dict() for o in self.outcomes],
                "rates": self.rates}


class Trainer:
    def __init__(self, cfg: TrainConfig):
        self.cfg = cfg
        self.runs: list[Run] = []
        self.last_run: Run | None = None

    def _one(self, kind, solver, difficulty, seed, puzzle_id) -> TrainOutcome:
        t0 = time.time()
        try:
            k = KINDS[kind]; s = SOLVERS[kind][solver]
            puzzle = k.sample(difficulty, seed)
            attempt = s(puzzle, seed)
            ok = bool(k.verify(puzzle, attempt))
            d = _h(kind, solver, difficulty, str(seed), str(puzzle_id),
                   "pass" if ok else "fail")
            return TrainOutcome(kind, solver, difficulty, puzzle_id,
                                ok, (time.time() - t0) * 1000.0, d)
        except Exception as e:
            d = _h(kind, solver, difficulty, str(seed), type(e).__name__)
            return TrainOutcome(kind, solver, difficulty, puzzle_id,
                                False, (time.time() - t0) * 1000.0, d)

    def run_once(self, index: int) -> Run:
        t0 = time.time()
        jobs = []
        for kind in self.cfg.kinds:
            for solver in sorted(SOLVERS.get(kind, {}).keys()):
                for difficulty in self.cfg.difficulties:
                    for pid in range(self.cfg.puzzles_per_tile):
                        jobs.append((kind, solver, difficulty,
                                     self.cfg.seed + index, pid))
        outcomes = [self._one(*j) for j in jobs]
        agg = {}
        for o in outcomes:
            k = (o.kind, o.solver, o.difficulty)
            cell = agg.setdefault(k, [0, 0]); cell[0] += 1
            if o.passed: cell[1] += 1
        tiles = [TrainTile(kind=k, solver=s, difficulty=d, trials=n, passes=p)
                 for (k, s, d), (n, p) in sorted(agg.items())]
        digest = _h("run", str(index), *sorted(t.digest for t in outcomes))
        parent_id = self.last_run.digest if self.last_run else None
        run = Run(index=index, tiles=tiles, outcomes=outcomes,
                  duration_ms=(time.time() - t0) * 1000.0,
                  digest=digest, parent_id=parent_id)
        self.last_run = run
        self.runs.append(run)
        return run

    def step(self, index: int) -> Run:
        run = self.run_once(index)
        self.cfg = _evolve(self.cfg, run, index)
        return run


def _evolve(cfg, prev, index):
    all_diff = ["easy", "medium", "hard"]
    new_diff = [all_diff[index % 3], all_diff[(index + 1) % 3]]
    kinds = list(cfg.kinds) or ["sudoku"]
    return replace(cfg, kinds=kinds, difficulties=new_diff,
                   puzzles_per_tile=min(cfg.puzzles_per_tile + 1, 8))
