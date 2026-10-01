"""Puzzles — reference requirements."""

from dcs.generate import requirement


@requirement(
    id="DCS-PUZ-001",
    title="scramble never returns SOLVED",
    section="puzzles",
    hats=["SCI", "FM"],
    criticality="MUST",
)
def scramble_safe():
    from app.puzzles.rubik import SOLVED, scramble

    for d in (2, 4, 6, 8, 10, 11):
        assert scramble(n_moves=d, seed=42) != SOLVED, d


@requirement(
    id="DCS-PUZ-002",
    title="solve_cube round-trips",
    section="puzzles",
    hats=["SCI", "MLE"],
    criticality="MUST",
)
def solve_round_trip():
    from app.puzzles.rubik import MOVES, SOLVED, apply_move, scramble, solve_cube

    for d in (2, 4, 6, 8, 10, 11):
        s = scramble(n_moves=d, seed=42)
        r = solve_cube(s)
        cur = s
        for m in r["solution"]:
            cur = apply_move(MOVES[m], cur)
        assert cur == SOLVED, d
