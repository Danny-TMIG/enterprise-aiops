"""Graph metrics from connectomics. Operates on MeshGraph."""
from __future__ import annotations

import collections
from itertools import combinations
from typing import Any

try:
    import numpy as np
    _HAVE_NP = True
except Exception:
    _HAVE_NP = False


def _index(nodes):
    return {n.id: i for i, n in enumerate(nodes)}


def adjacency(nodes, edges):
    idx = _index(nodes)
    n = len(nodes)
    if _HAVE_NP:
        A = np.zeros((n, n), dtype=float)
        for e in edges:
            i, j = idx.get(e.src), idx.get(e.dst)
            if i is None or j is None or i == j:
                continue
            A[i, j] = 1.0
            A[j, i] = 1.0
        return A, idx
    A = [dict() for _ in range(n)]
    for e in edges:
        i, j = idx.get(e.src), idx.get(e.dst)
        if i is None or j is None or i == j:
            continue
        A[i][j] = 1.0
        A[j][i] = 1.0
    return A, idx


def laplacian(nodes, edges):
    A, idx = adjacency(nodes, edges)
    if _HAVE_NP:
        D = np.diag(A.sum(axis=1))
        return D - A, A, idx
    n = len(nodes)
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        D[i][i] = sum(A[i].values())
    L = [[D[i][j] - A[i].get(j, 0.0) for j in range(n)] for i in range(n)]
    return L, A, idx


def fiedler(nodes, edges) -> dict[str, Any]:
    if not _HAVE_NP:
        return {"available": False, "reason": "numpy missing"}
    L, _, _ = laplacian(nodes, edges)
    if L.size == 0:
        return {"available": False, "reason": "empty graph"}
    w = np.sort(np.linalg.eigvalsh(L))
    lam2 = float(w[1]) if len(w) > 1 else 0.0
    return {
        "available": True,
        "nodes": int(L.shape[0]),
        "lambda_2": round(lam2, 6),
        "connected": lam2 > 1e-9,
    }


def modularity(nodes, edges, attr: str = "kind") -> dict[str, Any]:
    if not _HAVE_NP:
        return {"available": False, "reason": "numpy missing"}
    A, _ = adjacency(nodes, edges)
    n = A.shape[0]
    if n == 0:
        return {"available": True, "Q": 0.0, "m": 0}
    k = A.sum(axis=1)
    m2 = float(k.sum())
    if m2 <= 0:
        return {"available": True, "Q": 0.0, "m": 0}
    comm = [getattr(o, attr, None) or getattr(o, "kind", "?")
            for o in nodes]
    same = np.zeros((n, n))
    for i in range(n):
        same[i] = [1.0 if comm[i] == comm[j] else 0.0 for j in range(n)]
    B = A - np.outer(k, k) / m2
    Q = float((B * same).sum() / m2)
    return {"available": True, "Q": round(Q, 4),
            "m": int(m2 // 2), "communities": len(set(comm))}


def clustering_and_path(nodes, edges) -> dict[str, Any]:
    if not _HAVE_NP:
        return {"available": False, "reason": "numpy missing"}
    A, _ = adjacency(nodes, edges)
    n = A.shape[0]
    if n < 3:
        return {"available": False, "reason": "graph too small"}

    C = 0.0
    for i in range(n):
        nb = list(np.where(A[i] > 0)[0])
        d = len(nb)
        if d < 2:
            continue
        links = sum(1 for a, b in combinations(nb, 2) if A[a, b] > 0)
        C += 2 * links / (d * (d - 1))
    C /= n

    total, count = 0, 0
    for s in range(n):
        dist = {s: 0}
        q = collections.deque([s])
        while q:
            u = q.popleft()
            for v in np.where(A[u] > 0)[0]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        for v, dd in dist.items():
            if v != s:
                total += dd
                count += 1
    L_bar = (total / count) if count else None
    return {
        "available": True,
        "C": round(C, 4),
        "L_bar": round(L_bar, 4) if L_bar is not None else None,
        "reachable_pairs": count,
        "max_pairs": n * (n - 1),
    }
