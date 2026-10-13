"""Tic-tac-toe as a decision tree."""
from __future__ import annotations

from dataclasses import dataclass

from app.puzzles.tree import DecisionTree

EMPTY = 0
X = 1
O = 2

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
    (0, 4, 8), (2, 4, 6),              # diagonals
]


@dataclass(frozen=True)
class TTState:
    board: tuple[int, ...]
    to_move: int   # X or O

    def winner(self) -> int | None:
        for a, b, c in WIN_LINES:
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def full(self) -> bool:
        return all(v != EMPTY for v in self.board)


@dataclass
class TicTacToe(DecisionTree):
    def initial(self) -> TTState:
        return TTState(board=(EMPTY,) * 9, to_move=X)

    def actions(self, s: TTState) -> list[int]:
        return [i for i, v in enumerate(s.board) if v == EMPTY]

    def apply(self, s: TTState, a: int) -> TTState:
        b = list(s.board)
        b[a] = s.to_move
        return TTState(board=tuple(b), to_move=O if s.to_move == X else X)

    def is_terminal(self, s: TTState) -> bool:
        return s.winner() is not None or s.full()

    def reward(self, s: TTState, player: int) -> float:
        w = s.winner()
        if w is None:
            return 0.0
        # reward is from X's perspective when player=1; flip otherwise
        return 1.0 if w == X else -1.0

    def heuristic(self, s: TTState, player: int) -> float:
        w = s.winner()
        if w == X: return 1.0
        if w == O: return -1.0
        return 0.0


def demo() -> dict:
    from app.puzzles.tree import alpha_beta
    t = TicTacToe()
    r = alpha_beta(t, max_depth=9)
    return {
        "best_first_move": r.best_action,
        "value": r.reward,
        "nodes": r.nodes,
    }
