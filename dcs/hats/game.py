"""GAME — game. Tic-tac-toe minimax optimality."""
from dcs.generate import requirement

WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def winner(b):
    for a,b_,c in WIN_LINES:
        if b[a] and b[a] == b[b_] == b[c]: return b[a]
    return None

def minimax(b, me):
    w = winner(b)
    if w == me: return 1, None
    if w:       return -1, None
    if all(b):  return 0, None
    other = "O" if me == "X" else "X"
    best = -2; move = None
    for i, v in enumerate(b):
        if not v:
            b[i] = me; s, _ = minimax(b, other); b[i] = ""
            s = -s
            if s > best: best, move = s, i
    return best, move

@requirement(id="DCS-GAME-001", title="minimax never loses from an empty board",
             section="GAME.game", hats=["GAME"], criticality="MUST")
def test():
    _, move = minimax(list("") * 0 + [""]*9, "X")
    assert move in range(9)
    # from empty board, X must not score negative against perfect play
    score, _ = minimax([""]*9, "X")
    assert score >= 0

