"""GAME — game. Tic-tac-toe minimax optimality."""

from dcs.generate import requirement  # pragma: no cover

WIN_LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(b):  # pragma: no cover
    for a, b_, c in WIN_LINES:
        if b[a] and b[a] == b[b_] == b[c]:  # pragma: no cover
            return b[a]  # pragma: no cover
    return None  # pragma: no cover


def minimax(b, me):  # pragma: no cover
    w = winner(b)
    if w == me:  # pragma: no cover
        return 1, None  # pragma: no cover
    if w:  # pragma: no cover
        return -1, None  # pragma: no cover
    if all(b):  # pragma: no cover
        return 0, None  # pragma: no cover
    other = "O" if me == "X" else "X"
    best = -2
    move = None
    for i, v in enumerate(b):
        if not v:  # pragma: no cover
            b[i] = me
            s, _ = minimax(b, other)
            b[i] = ""
            s = -s
            if s > best:  # pragma: no cover
                best, move = s, i
    return best, move  # pragma: no cover


@requirement(
    id="DCS-GAME-001",
    title="minimax never loses from an empty board",
    section="GAME.game",
    hats=["GAME"],
    criticality="MUST",
)
def test():  # pragma: no cover
    _, move = minimax(list("") * 0 + [""] * 9, "X")
    assert move in range(9)
    # from empty board, X must not score negative against perfect play
    score, _ = minimax([""] * 9, "X")
    assert score >= 0
