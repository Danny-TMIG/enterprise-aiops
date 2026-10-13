"""Configurator: pick the puzzle shape and the constraint set.

Kinds: sudoku | crossword | rubik | tictactoe | gridworld.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.puzzles.atlas import load_atlas
from app.puzzles.crossword import (
    make_crossword,
)
from app.puzzles.sudoku import make_sudoku

KINDS = ("sudoku", "crossword", "rubik", "tictactoe", "gridworld")


@dataclass
class Config:
    kind: str = "sudoku"
    difficulty: str = "medium"
    categories: list[str] = field(default_factory=list)
    seed: int = 0
    meta: dict = field(default_factory=dict)

    def validate(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown kind: {self.kind}")
        if self.difficulty not in ("easy", "medium", "hard"):
            raise ValueError(f"unknown difficulty: {self.difficulty}")


_EASY_GIVENS = [
    (0,0,5),(0,1,3),(0,2,4),(0,4,7),(0,6,9),(0,8,2),
    (1,0,6),(1,3,1),(1,4,9),(1,5,5),(1,8,4),
    (2,1,9),(2,2,8),(2,7,6),(2,3,4),(2,5,3),
    (3,0,8),(3,4,6),(3,8,3),(3,2,7),(3,6,1),
    (4,0,4),(4,3,8),(4,5,3),(4,8,1),(4,1,5),
    (5,0,7),(5,4,2),(5,8,6),(5,2,1),(5,6,8),
    (6,1,6),(6,6,2),(6,7,8),(6,4,7),
    (7,3,4),(7,4,1),(7,5,9),(7,8,5),(7,0,2),
    (8,4,8),(8,7,7),(8,8,9),(8,2,1),
]

_MEDIUM_GIVENS = [
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

_HARD_GIVENS = [
    (0,0,5),(0,4,7),
    (1,3,1),(1,5,5),
    (2,1,9),(2,7,6),
    (3,4,6),(3,8,3),
    (4,3,8),(4,5,3),
    (5,0,7),(5,4,2),
    (6,1,6),(6,7,8),
    (7,3,4),(7,8,5),
    (8,4,8),(8,8,9),
]


def configure(cfg: Config) -> dict:
    cfg.validate()

    if cfg.kind == "sudoku":
        givens = {"easy": _EASY_GIVENS, "medium": _MEDIUM_GIVENS,
                  "hard": _HARD_GIVENS}[cfg.difficulty]
        puzzle = make_sudoku(givens=givens, seed=cfg.seed)
        return {"kind": "sudoku", "puzzle": puzzle, "givens": len(givens)}

    if cfg.kind == "crossword":
        atlas = load_atlas()
        puzzle = make_crossword(atlas=atlas, seed=cfg.seed)
        return {"kind": "crossword", "puzzle": puzzle,
                "pool": puzzle.pool_size}

    if cfg.kind == "rubik":
        from app.puzzles.rubik import scramble
        depth = {"easy": 6, "medium": 9, "hard": 11}[cfg.difficulty]
        state = scramble(n_moves=depth, seed=cfg.seed)
        return {"kind": "rubik", "state": state, "scramble_depth": depth}

    if cfg.kind == "tictactoe":
        from app.puzzles.tictactoe import TicTacToe
        return {"kind": "tictactoe", "tree": TicTacToe()}

    if cfg.kind == "gridworld":
        from app.puzzles.gridworld import Gridworld
        return {"kind": "gridworld", "tree": Gridworld()}

    raise RuntimeError("unreachable")


def reconfig(cfg: Config, change: dict) -> Config:
    new = Config(
        kind=change.get("kind", cfg.kind),
        difficulty=change.get("difficulty", cfg.difficulty),
        categories=list(change.get("categories", cfg.categories)),
        seed=change.get("seed", cfg.seed + 1),
        meta=dict(cfg.meta),
    )
    new.validate()
    return new


@dataclass
class Configurator:
    history: list[Config] = field(default_factory=list)

    def configure(self, cfg: Config) -> dict:
        self.history.append(cfg)
        return configure(cfg)

    def reconfig(self, change: dict) -> dict:
        if not self.history:
            raise RuntimeError("no prior config")
        new = reconfig(self.history[-1], change)
        self.history.append(new)
        return configure(new)

    def undo(self) -> Config | None:
        if len(self.history) < 2:
            return None
        self.history.pop()
        return self.history[-1]

    def to_dict(self):
        return {"history": [
            {"kind": c.kind, "difficulty": c.difficulty, "seed": c.seed}
            for c in self.history
        ]}
