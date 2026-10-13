"""Mesh operations. Canonical — do not edit in place."""
from __future__ import annotations

import hashlib
from typing import Any


def weave(*args) -> dict[str, Any]:
    runs = list(args[0]) if len(args) == 1 and isinstance(args[0], (list, tuple)) else list(args)
    return {"runs": len(runs),
            "outcomes": sum(len(getattr(r, "outcomes", [])) for r in runs),
            "digests": [getattr(r, "digest", None) for r in runs]}


def criss_cross(a, b) -> dict[str, Any]:
    h = hashlib.sha256(((getattr(a, "digest", "") or "") + "|" +
                        (getattr(b, "digest", "") or "")).encode()).hexdigest()
    return {"a_index": getattr(a, "index", None),
            "b_index": getattr(b, "index", None),
            "a_digest": getattr(a, "digest", None),
            "b_digest": getattr(b, "digest", None),
            "combined": "sha256:" + h[:16], "length": len(h)}


def trans(runs, key_fn=None) -> dict[str, Any]:
    by_id = {}
    for i, r in enumerate(runs):
        rid = getattr(r, "id", None) or getattr(r, "digest", None) or str(i)
        by_id[rid] = r
    id_of = {rid: (key_fn(r) if key_fn else rid) for rid, r in by_id.items()}
    adj = {rid: set() for rid in by_id}
    edges = 0
    for rid, r in by_id.items():
        pid = getattr(r, "parent_id", None)
        if pid and pid in by_id:
            adj[pid].add(rid); edges += 1
    reach_sets = {}
    def visit(node, seen):
        if node in reach_sets: return reach_sets[node]
        out = set()
        for ch in adj.get(node, ()):
            if ch in seen: continue
            out.add(ch); out |= visit(ch, seen | {ch})
        reach_sets[node] = out
        return out
    for rid in by_id: visit(rid, {rid})
    reach = {id_of[rid]: sorted(id_of[c] for c in reach_sets.get(rid, set()))
             for rid in by_id}
    reachable = {k: len(v) for k, v in reach.items()}
    return {"digests": [getattr(r, "digest", None) for r in runs],
            "keys": list(id_of.values()), "edges": edges,
            "transitive_pairs": sum(reachable.values()),
            "reachable": reachable, "reach": reach}


def pollinate(a, b) -> list[dict[str, Any]]:
    ra = getattr(a, "rates", {}) or {}
    rb = getattr(b, "rates", {}) or {}
    ka, kb = set(ra), set(rb)
    out = []
    for k in sorted(kb - ka):
        out.append({"stream": k, "change": "added", "a": None,
                    "b": rb[k], "delta": None})
    for k in sorted(ka - kb):
        out.append({"stream": k, "change": "removed", "a": ra[k],
                    "b": None, "delta": None})
    for k in sorted(ka & kb):
        if ra[k] != rb[k]:
            out.append({"stream": k, "change": "changed",
                        "a": ra[k], "b": rb[k], "delta": rb[k] - ra[k]})
    return out


class MeshOfMeshes:
    def __init__(self, runs=None):
        self.runs = list(runs or [])
    def add(self, run):
        self.runs.append(run); return self
    def add_run(self, run) -> None:
        self.runs.append(run)
    def weave(self):
        return weave(self.runs)
    def trans(self, key_fn=None):
        return trans(self.runs, key_fn=key_fn)
    def criss_cross(self, a=None, b=None):
        if a is None or b is None:
            if len(self.runs) < 2: return {"combined": None, "length": 0}
            a, b = self.runs[-2], self.runs[-1]
        return criss_cross(a, b)
    def pollinate(self, a=None, b=None):
        if a is None or b is None:
            if len(self.runs) < 2: return []
            a, b = self.runs[-2], self.runs[-1]
        return pollinate(a, b)
    def to_dict(self):
        total = sum(len(getattr(r, "outcomes", [])) for r in self.runs)
        return {"runs": len(self.runs), "size": total, "n_runs": len(self.runs),
                "outcomes": total,
                "digests": [getattr(r, "digest", None) for r in self.runs],
                "indices": [getattr(r, "index", None) for r in self.runs]}
    def __len__(self): return len(self.runs)
    def __iter__(self): return iter(self.runs)
