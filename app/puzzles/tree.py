"""Generic decision tree + solvers.

A DecisionTree is:
    initial() -> State
    actions(state) -> list[Action]
    apply(state, action) -> State
    is_terminal(state) -> bool
    reward(state, player) -> float     # player = +1 or -1
    heuristic(state, player) -> float  # optional

Solvers:
    bfs             - shortest path to terminal
    ida_star        - depth-first with a heuristic
    minimax         - perfect-info 2-player
    alpha_beta      - minimax with pruning
    mcts            - Monte Carlo tree search

All solvers take a tree and return a `SearchResult` with the
winning path (or best move) plus a node count.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Protocol

State = Any
Action = Any


class DecisionTree(Protocol):
    def initial(self) -> State: ...
    def actions(self, s: State) -> list[Action]: ...
    def apply(self, s: State, a: Action) -> State: ...
    def is_terminal(self, s: State) -> bool: ...
    def reward(self, s: State, player: int) -> float: ...
    def heuristic(self, s: State, player: int) -> float: ...


@dataclass
class SearchResult:
    found: bool
    path: list[Action] = field(default_factory=list)
    terminal_state: State | None = None
    reward: float = 0.0
    nodes: int = 0
    depth: int = 0
    best_action: Action | None = None

    def to_dict(self) -> dict:
        return {
            "found": self.found,
            "path": [str(a) for a in self.path],
            "reward": self.reward,
            "nodes": self.nodes,
            "depth": self.depth,
            "best_action": str(self.best_action) if self.best_action is not None else None,
        }


def _default_heuristic(s, player):
    return 0.0


# ── BFS ─────────────────────────────────────────────────────────
def bfs(tree: DecisionTree, max_nodes: int = 1_000_000) -> SearchResult:
    from collections import deque
    start = tree.initial()
    if tree.is_terminal(start):
        return SearchResult(found=True, terminal_state=start,
                            reward=tree.reward(start, 1), depth=0)
    seen = {start}
    q = deque([(start, [], 1)])   # (state, path, player-to-move)
    nodes = 0
    while q:
        s, path, player = q.popleft()
        nodes += 1
        if nodes > max_nodes:
            return SearchResult(found=False, nodes=nodes)
        for a in tree.actions(s):
            ns = tree.apply(s, a)
            np = -player
            new_path = path + [a]
            if tree.is_terminal(ns):
                return SearchResult(
                    found=True, path=new_path, terminal_state=ns,
                    reward=tree.reward(ns, 1), nodes=nodes,
                    depth=len(new_path),
                )
            if ns not in seen:
                seen.add(ns)
                q.append((ns, new_path, np))
    return SearchResult(found=False, nodes=nodes)


# ── IDA* ────────────────────────────────────────────────────────
def ida_star(tree: DecisionTree, max_depth: int = 64,
             max_nodes: int = 1_000_000) -> SearchResult:
    nodes = [0]
    bound = [tree.heuristic(tree.initial(), 1)]

    def search(s, path, g, bound, player):
        f = g + tree.heuristic(s, player)
        if f > bound[0]:
            return f, None
        if tree.is_terminal(s):
            return -1, SearchResult(
                found=True, path=list(path), terminal_state=s,
                reward=tree.reward(s, 1), nodes=nodes[0],
                depth=len(path),
            )
        mn = math.inf
        for a in tree.actions(s):
            nodes[0] += 1
            if nodes[0] > max_nodes:
                return math.inf, None
            ns = tree.apply(s, a)
            path.append(a)
            t, res = search(ns, path, g + 1, bound, -player)
            path.pop()
            if res is not None:
                return -1, res
            mn = min(mn, t)
        return mn, None

    start = tree.initial()
    while bound[0] <= max_depth:
        t, res = search(start, [], 0, bound, 1)
        if res is not None:
            res.nodes = nodes[0]
            return res
        if t == math.inf:
            return SearchResult(found=False, nodes=nodes[0])
        bound[0] = t
    return SearchResult(found=False, nodes=nodes[0])


# ── minimax ─────────────────────────────────────────────────────
def minimax(tree: DecisionTree, max_depth: int = 32
            ) -> SearchResult:
    nodes = [0]

    def mm(s, depth, player):
        nodes[0] += 1
        if tree.is_terminal(s) or depth == 0:
            return tree.reward(s, 1)
        vals = [mm(tree.apply(s, a), depth - 1, -player)
                for a in tree.actions(s)]
        if not vals:
            return tree.reward(s, 1)
        return max(vals) if player == 1 else min(vals)

    start = tree.initial()
    best_v = -math.inf
    best_a = None
    for a in tree.actions(start):
        v = mm(tree.apply(start, a), max_depth - 1, -1)
        if v > best_v:
            best_v = v
            best_a = a
    return SearchResult(
        found=True, best_action=best_a, reward=best_v,
        nodes=nodes[0], depth=0,
    )


# ── alpha-beta ──────────────────────────────────────────────────
def alpha_beta(tree: DecisionTree, max_depth: int = 32
               ) -> SearchResult:
    nodes = [0]

    def ab(s, depth, alpha, beta, player):
        nodes[0] += 1
        if tree.is_terminal(s) or depth == 0:
            return tree.reward(s, 1)
        if player == 1:
            v = -math.inf
            for a in tree.actions(s):
                v = max(v, ab(tree.apply(s, a), depth - 1, alpha, beta, -1))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return v
        else:
            v = math.inf
            for a in tree.actions(s):
                v = min(v, ab(tree.apply(s, a), depth - 1, alpha, beta, 1))
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v

    start = tree.initial()
    best_v = -math.inf
    best_a = None
    for a in tree.actions(start):
        v = ab(tree.apply(start, a), max_depth - 1,
               -math.inf, math.inf, -1)
        if v > best_v:
            best_v = v
            best_a = a
    return SearchResult(
        found=True, best_action=best_a, reward=best_v,
        nodes=nodes[0], depth=0,
    )


# ── MCTS ────────────────────────────────────────────────────────
@dataclass
class _Node:
    state: State
    player: int
    parent: _Node | None = None
    action: Action | None = None
    children: list[_Node] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0
    untried: list[Action] = field(default_factory=list)


def mcts(tree: DecisionTree, iterations: int = 2000,
         seed: int = 0) -> SearchResult:
    rng = random.Random(seed)

    def expand(n):
        if not n.untried:
            return n
        a = n.untried.pop(rng.randrange(len(n.untried)))
        ns = tree.apply(n.state, a)
        c = _Node(state=ns, player=-n.player, parent=n, action=a,
                  untried=tree.actions(ns))
        n.children.append(c)
        return c

    def simulate(n):
        s, p = n.state, n.player
        depth = 0
        while not tree.is_terminal(s) and depth < 64:
            acts = tree.actions(s)
            if not acts:
                break
            a = acts[rng.randrange(len(acts))]
            s = tree.apply(s, a)
            p = -p
            depth += 1
        return tree.reward(s, 1)

    def backprop(n, value):
        while n is not None:
            n.visits += 1
            n.value += value
            value = -value
            n = n.parent

    root = _Node(state=tree.initial(), player=1,
                 untried=tree.actions(tree.initial()))
    for _ in range(iterations):
        n = root
        while not n.untried and n.children:
            # UCB1
            logN = math.log(n.visits + 1)
            n = max(n.children,
                    key=lambda c: (c.value / (c.visits + 1e-9)
                                   + 1.4 * math.sqrt(logN / (c.visits + 1))))
        if n.untried:
            n = expand(n)
        v = simulate(n)
        backprop(n, v)
    if not root.children:
        return SearchResult(found=False)
    best = max(root.children, key=lambda c: c.visits)
    return SearchResult(
        found=True, best_action=best.action,
        reward=best.value / max(best.visits, 1),
        nodes=iterations,
    )
