"""Trans-all: the transitive closure of the prefix-extension DAG.

Nodes   = every chain over the alphabet
Edges   = c1 -> c2 iff c2 is c1 extended by exactly one letter
          (equivalently: c1 is a prefix of c2 and |c2| = |c1| + 1)

Transitive closure: c1 ⇝ c2 iff c1 is a prefix of c2.

Reachability from A: every chain whose head is A.
Reachability to Z:   every chain whose tail is Z.
A to Z:              every chain whose head is A and tail is Z.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator

from app.transchain.atoms import ALPHABET
from app.transchain.chain import Chain
from app.transchain.gen import all_chains


def prefix_edges(alpha: tuple[str, ...] = ALPHABET,
                 max_len: int | None = None
                 ) -> Iterator[tuple[Chain, Chain]]:
    top = max_len if max_len is not None else len(alpha)
    prev: list[Chain] = []
    for c in all_chains(alpha, max_len=top):
        if prev and len(prev[0]) == len(c):
            prev.append(c)
            continue
        if prev and len(c) == len(prev[0]) + 1:
            for p in prev:
                for x in alpha:
                    if x in p.seq:
                        continue
                    cand = p.extend(x)
                    if cand.seq == c.seq:
                        yield (p, c)
                        break
            prev.append(c)
        else:
            for p in prev:
                for x in alpha:
                    if x in p.seq:
                        continue
                    cand = p.extend(x)
                    yield (p, cand)
            prev = [c]


def _edges_simple(alpha: tuple[str, ...], max_len: int
                  ) -> list[tuple[Chain, Chain]]:
    """Direct: for each chain c and each letter x not in c, edge c -> c+x."""
    out: list[tuple[Chain, Chain]] = []
    for c in all_chains(alpha, max_len=max_len):
        for x in alpha:
            if x in c.seq:
                continue
            out.append((c, c.extend(x)))
    return out


def transitive_closure(alpha: tuple[str, ...] = ALPHABET,
                       max_len: int | None = None
                       ) -> dict[str, set[str]]:
    top = max_len if max_len is not None else len(alpha)
    reach: dict[str, set[str]] = defaultdict(set)
    edges = _edges_simple(alpha, top)
    adj: dict[str, list[str]] = defaultdict(list)
    nodes: set[str] = set()
    for u, v in edges:
        adj[u.id].append(v.id)
        nodes.add(u.id); nodes.add(v.id)

    for start in nodes:
        seen = set()
        stack = [start]
        while stack:
            u = stack.pop()
            for v in adj.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        reach[start] = seen
    return reach


def reachability(alpha: tuple[str, ...] = ALPHABET,
                 max_len: int | None = None,
                 head: str | None = None,
                 tail: str | None = None
                 ) -> Iterator[Chain]:
    top = max_len if max_len is not None else len(alpha)
    for c in all_chains(alpha, max_len=top):
        if head is not None and c.head != head:
            continue
        if tail is not None and c.tail != tail:
            continue
        yield c


def trans_all(alpha: tuple[str, ...] = ALPHABET,
              max_len: int | None = None
              ) -> dict[str, object]:
    top = max_len if max_len is not None else len(alpha)
    n = len(alpha)
    nodes = 0
    edges = 0
    by_len: dict[int, int] = {}
    for c in all_chains(alpha, max_len=top):
        nodes += 1
        by_len[len(c)] = by_len.get(len(c), 0) + 1
        edges += sum(1 for x in alpha if x not in c.seq)
    reach = transitive_closure(alpha, max_len=top)
    a_chains = sum(1 for c in all_chains(alpha, max_len=top) if c.head == alpha[0])
    z_chains = sum(1 for c in all_chains(alpha, max_len=top) if c.tail == alpha[-1])
    az_chains = sum(1 for c in all_chains(alpha, max_len=top)
                    if c.head == alpha[0] and c.tail == alpha[-1])
    return {
        "alphabet": alpha,
        "max_len": top,
        "nodes": nodes,
        "edges": edges,
        "by_len": by_len,
        "transitive_pairs": sum(len(v) for v in reach.values()),
        "chains_from_A": a_chains,
        "chains_to_Z": z_chains,
        "chains_A_to_Z": az_chains,
    }
