"""Small gridworld with a key and a locked door.

Single-player decision tree with a terminal goal. BFS finds the
shortest path. Not adversarial, so minimax doesn't apply — this
is the "video game" side of the pair.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.puzzles.tree import DecisionTree

WALL = "#"
FLOOR = "."
KEY = "K"
DOOR = "D"
GOAL = "G"


@dataclass(frozen=True)
class GWState:
    x: int
    y: int
    has_key: bool
    door_open: bool


@dataclass
class Gridworld(DecisionTree):
    layout: tuple[str, ...] = (
        "#########",
        "#.......#",
        "#..K....#",
        "#.......#",
        "#.....D.#",
        "#.......#",
        "#.......#",
        "#.....G.#",
        "#########",
    )

    def _cell(self, x: int, y: int) -> str:
        return self.layout[y][x]

    def initial(self) -> GWState:
        return GWState(x=1, y=1, has_key=False, door_open=False)

    def actions(self, s: GWState) -> list[str]:
        if self.is_terminal(s):
            return []
        acts = []
        for d, (dx, dy) in (("N", (0, -1)), ("S", (0, 1)),
                            ("E", (1, 0)), ("W", (-1, 0))):
            nx, ny = s.x + dx, s.y + dy
            if self._cell(nx, ny) == WALL:
                continue
            if self._cell(nx, ny) == DOOR and not s.door_open:
                continue
            acts.append(d)
        if self._cell(s.x, s.y) == KEY and not s.has_key:
            acts.append("pick")
        if (self._cell(s.x, s.y) == DOOR and s.has_key
                and not s.door_open):
            acts.append("open")
        return acts

    def apply(self, s: GWState, a: str) -> GWState:
        if a == "pick":
            return GWState(s.x, s.y, has_key=True, door_open=s.door_open)
        if a == "open":
            return GWState(s.x, s.y, has_key=s.has_key, door_open=True)
        dx, dy = {"N": (0, -1), "S": (0, 1),
                  "E": (1, 0), "W": (-1, 0)}[a]
        nx, ny = s.x + dx, s.y + dy
        return GWState(nx, ny, has_key=s.has_key, door_open=s.door_open)

    def is_terminal(self, s: GWState) -> bool:
        return self._cell(s.x, s.y) == GOAL

    def reward(self, s: GWState, player: int) -> float:
        return 100.0 if self.is_terminal(s) else -1.0

    def heuristic(self, s: GWState, player: int) -> float:
        # manhattan distance to the goal
        gx = gy = -1
        for y, row in enumerate(self.layout):
            for x, c in enumerate(row):
                if c == GOAL:
                    gx, gy = x, y
        return abs(s.x - gx) + abs(s.y - gy)
