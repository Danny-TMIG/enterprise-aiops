"""Demo: atlas, sudoku, crossword, rubik, tictactoe, gridworld."""
from __future__ import annotations

import sys

from app.puzzles.atlas import load_atlas
from app.puzzles.configurator import Config, Configurator
from app.puzzles.crossword import make_crossword, solve_crossword
from app.puzzles.gridworld import Gridworld
from app.puzzles.rubik import scramble, solve_cube
from app.puzzles.sudoku import make_sudoku, solve_sudoku
from app.puzzles.tictactoe import TicTacToe
from app.puzzles.tree import alpha_beta, bfs, mcts


def _hdr(t):
    print("=" * 68)
    print("  " + t)
    print("=" * 68)


def demo_rubik():
    _hdr("rubik 2x2 (8-corner decision tree)")
    for depth in (4, 6, 8, 10):
        state = scramble(n_moves=depth, seed=42)
        r = solve_cube(state, max_depth=20, max_nodes=200_000)
        mark = "OK" if r["solved"] else "  "
        n = r.get("nodes", 0)
        ln = r.get("solution_len", "-")
        print(f"  [{mark}] scramble depth {depth:2d}  "
              f"solution len {ln}  nodes {n}")
    print()


def demo_tictactoe():
    _hdr("tic-tac-toe (perfect-info adversarial)")
    t = TicTacToe()
    r = alpha_beta(t, max_depth=9)
    print(f"  alpha_beta: best first move = {r.best_action}, "
          f"value = {r.reward}, nodes = {r.nodes}")
    r2 = mcts(t, iterations=2000, seed=1)
    print(f"  mcts:      best first move = {r2.best_action}, "
          f"value = {r2.reward:.3f}, nodes = {r2.nodes}")
    print()


def demo_gridworld():
    _hdr("gridworld (single-player shortest path)")
    g = Gridworld()
    r = bfs(g)
    if r.found:
        print(f"  solved in {r.depth} actions, {r.nodes} nodes")
        print(f"  path: {' '.join(str(a) for a in r.path)}")
    else:
        print(f"  unsolved, {r.nodes} nodes")
    print()


def demo_sudoku():
    _hdr("sudoku (constraint grid)")
    p = make_sudoku(seed=1)
    r = solve_sudoku(p)
    if r["solved"]:
        print(f"  solved in {r['nodes']} nodes")
    else:
        print(f"  unsolved: {r['nodes']} nodes")
    print()


def demo_crossword():
    _hdr("crossword (atlas as lexicon)")
    a = load_atlas()
    p = make_crossword(atlas=a, seed=1)
    r = solve_crossword(p)
    if r["solved"]:
        print(f"  solved in {r['nodes']} nodes")
        for slot in p.slots:
            print(f"    {slot.id} = {r['assignment'].get(slot.id)}")
    else:
        print(f"  unsolved: {r['nodes']} nodes")
    print()


def demo_configurator():
    _hdr("configurator — five kinds")
    c = Configurator()
    print("  configure sudoku/easy   ->",
          "givens =", c.configure(Config(kind="sudoku",
                                          difficulty="easy"))["givens"])
    print("  reconfig -> rubik/hard  ->",
          "scramble depth =",
          c.reconfig({"kind": "rubik", "difficulty": "hard"})["scramble_depth"])
    print("  reconfig -> tictactoe   ->",
          "kind =", c.reconfig({"kind": "tictactoe"})["kind"])
    print("  reconfig -> gridworld   ->",
          "kind =", c.reconfig({"kind": "gridworld"})["kind"])
    print("  reconfig -> crossword   ->",
          "pool =", c.reconfig({"kind": "crossword"})["pool"])
    print("  undo                    -> kind =",
          c.undo().kind)
    print("  history:")
    for h in c.to_dict()["history"]:
        print(f"    {h}")
    print()


def main():
    demo_rubik()
    demo_tictactoe()
    demo_gridworld()
    demo_sudoku()
    demo_crossword()
    demo_configurator()
    print("=" * 68)
    print("  Sudoku, crossword, rubik, tic-tac-toe, gridworld: one")
    print("  decision-tree protocol, five instantiations, four")
    print("  solvers (bfs, ida_star, alpha_beta, mcts).")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
