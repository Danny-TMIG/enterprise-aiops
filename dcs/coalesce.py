"""Coalescence operations project-wide.

Every operation:
    merge(kind, a, b) -> Merged(value, sources)

Properties (where declared):
    COMMUTATIVE   merge(a,b) ≡ merge(b,a) up to equivalence
    IDEMPOTENT    merge(a,a) ≡ a
    PROVENANCE    sources carries every contributor id
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from dcs.equivalence import canonical_key


@dataclass
class Merged:
    value: Any
    sources: Tuple[str, ...] = ()

    def with_source(self, *ids: str) -> "Merged":
        return Merged(self.value, self.sources + tuple(ids))


_OP: Dict[str, Callable[[Any, Any], Merged]] = {}


def register(kind: str, fn: Callable[[Any, Any], Merged]) -> None:
    _OP[kind] = fn


def merge(kind: str, a: Any, b: Any) -> Merged:
    if kind not in _OP:
        raise KeyError(f"no coalescence operation for {kind!r}")
    return _OP[kind](a, b)


def ops() -> list[str]:
    return sorted(_OP.keys())


def provenance(m: Merged) -> dict:
    return {"sources": list(m.sources), "value_kind": type(m.value).__name__}


# ── helpers ────────────────────────────────────────────────────────
def _union_list(a, b):
    seen, out = set(), []
    for x in list(a or []) + list(b or []):
        k = canonical_key("JSON", x)
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
    return out


def _merge_dict_last_wins(a, b):
    return {**a, **b}


def _merge_dict_sum(a, b):
    ca, cb = Counter(a or {}), Counter(b or {})
    return dict(ca + cb)


def _max_float(a, b):
    return max(a or 0.0, b or 0.0)


def _min_float(a, b):
    return min(a or 0.0, b or 0.0)


# ── TrainTile ──────────────────────────────────────────────────────
def _tile_merge(a, b):
    from app.train.core import TrainTile
    if (a.kind, a.solver, a.difficulty) != (b.kind, b.solver, b.difficulty):
        raise ValueError(f"cannot coalesce {a.kind} with {b.kind}")
    return Merged(TrainTile(
        kind=a.kind, solver=a.solver, difficulty=a.difficulty,
        trials=a.trials + b.trials,
        passes=a.passes + b.passes,
        duration_ms=max(a.duration_ms, b.duration_ms),
    ), sources=(canonical_key("TrainTile", a),))


register("TrainTile", _tile_merge)


def _tile_list_merge(a, b):
    by_key = {}
    for t in list(a) + list(b):
        k = (t.kind, t.solver, t.difficulty)
        if k in by_key:
            by_key[k] = _tile_merge(by_key[k], t).value
        else:
            by_key[k] = t
    return Merged(list(by_key.values()), sources=())


register("TileList", _tile_list_merge)


# ── TrainOutcome ───────────────────────────────────────────────────
def _outcome_merge(a, b):
    if (a.kind, a.solver, a.difficulty, a.puzzle_id) != \
       (b.kind, b.solver, b.difficulty, b.puzzle_id):
        raise ValueError("outcome identity mismatch")
    if a.passed and b.passed:
        winner = a if a.duration_ms <= b.duration_ms else b
    else:
        winner = a if not a.passed else b
    return Merged(winner, sources=(a.digest, b.digest))


register("TrainOutcome", _outcome_merge)


def _outcome_list_merge(a, b):
    seen, out = set(), []
    for o in list(a) + list(b):
        if o.digest in seen:
            continue
        seen.add(o.digest)
        out.append(o)
    return Merged(out, sources=tuple(seen))


register("OutcomeList", _outcome_list_merge)


# ── Run ────────────────────────────────────────────────────────────
def _runs_agree(a, b):
    ra, rb = a.rates, b.rates
    if set(ra) != set(rb):
        return False
    return all(abs(ra[k] - rb[k]) < 1e-12 for k in ra)


def _run_merge(a, b):
    from app.train.core import Run
    if not _runs_agree(a, b):
        raise ValueError(f"runs disagree: {a.digest} vs {b.digest}")
    winner = a if len(a.tiles) >= len(b.tiles) else b
    merged = Run(
        index=min(a.index, b.index),
        tiles=list(winner.tiles),
        outcomes=list(winner.outcomes),
        duration_ms=max(a.duration_ms, b.duration_ms),
        digest=winner.digest,
        parent_id=winner.parent_id,
    )
    return Merged(merged, sources=(a.digest, b.digest))


register("Run", _run_merge)


def _runs_seq_merge(a, b):
    seen, out = set(), []
    for r in list(a) + list(b):
        if r.digest in seen:
            continue
        seen.add(r.digest)
        out.append(r)
    return Merged(out, sources=tuple(seen))


register("RunSequence", _runs_seq_merge)


# ── MeshOfMeshes ───────────────────────────────────────────────────
def _mesh_merge(a, b):
    from app.train.mesh import MeshOfMeshes
    seen, runs = set(), []
    for r in list(a.runs) + list(b.runs):
        if r.digest in seen:
            continue
        seen.add(r.digest)
        runs.append(r)
    return Merged(MeshOfMeshes(runs), sources=tuple(seen))


register("MeshOfMeshes", _mesh_merge)


# ── CrissCross ─────────────────────────────────────────────────────
def _cc_merge(a, b):
    def key(d):
        return tuple(sorted((d.get("a_digest") or "",
                             d.get("b_digest") or "")))
    winner = a if key(a) <= key(b) else b
    return Merged(winner, sources=(winner.get("combined") or "",))


register("CrissCross", _cc_merge)


# ── Pollinate ──────────────────────────────────────────────────────
def _pl_merge(a, b):
    seen, out = set(), []
    for p in list(a) + list(b):
        k = (p["stream"], p["change"])
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    return Merged(out, sources=())


register("Pollinate", _pl_merge)


# ── Requirement / Standard ─────────────────────────────────────────
def _req_merge(a, b):
    from dcs.standard import Requirement
    if a.id != b.id:
        raise ValueError(f"requirement id mismatch: {a.id} vs {b.id}")
    order = {"MUST": 2, "SHOULD": 1, "MAY": 0}
    crit = a.criticality if order[a.criticality] >= order[b.criticality] \
                          else b.criticality
    return Merged(Requirement(
        id=a.id, title=a.title or b.title, section=a.section,
        hats=sorted(set(a.hats) | set(b.hats)),
        criticality=crit, test=a.test or b.test,
    ), sources=(a.id,))


register("Requirement", _req_merge)


def _std_merge(a, b):
    from dcs.standard import Standard
    by_id = {}
    for r in list(a.requirements) + list(b.requirements):
        if r.id in by_id:
            by_id[r.id] = _req_merge(by_id[r.id], r).value
        else:
            by_id[r.id] = r
    return Merged(Standard(
        id=a.id, version=a.version, title=a.title,
        published=a.published, authority=a.authority,
        requirements=sorted(by_id.values(), key=lambda r: r.id),
    ), sources=(a.ref, b.ref))


register("Standard", _std_merge)


# ── Bundle ─────────────────────────────────────────────────────────
def _bundle_merge(a, b):
    if a.get("standard_ref") != b.get("standard_ref"):
        raise ValueError(f"bundle standard mismatch: "
                         f"{a.get('standard_ref')} vs {b.get('standard_ref')}")
    by_id = {}
    for r in a.get("results", []):
        by_id[r["id"]] = r
    for r in b.get("results", []):
        prev = by_id.get(r["id"])
        if prev is None or prev.get("pass"):
            by_id[r["id"]] = r
    from dcs.evidence import Bundle, RequirementResult
    results = [
        RequirementResult(
            id=r["id"], criticality=r["criticality"],
            pass_=bool(r["pass"]),
            duration_ms=r.get("duration_ms", 0.0),
            detail=r.get("detail", ""),
            evidence=r.get("evidence", ""),
            error=r.get("error"),
        )
        for _, r in sorted(by_id.items())
    ]
    merged = Bundle(
        standard_ref=a["standard_ref"],
        reference=dict(a["reference"]),
        started=min(a["started"], b["started"]),
        completed=max(a["completed"], b["completed"]),
        results=results,
    ).seal()
    return Merged(merged, sources=(a.get("digest") or "",
                                   b.get("digest") or ""))


register("Bundle", _bundle_merge)


# ── LogEntry / LogChain ────────────────────────────────────────────
def _log_merge(a, b):
    return Merged(a, sources=(a.get("entry_hash") or "",))


register("LogEntry", _log_merge)


def _log_chain_merge(a, b):
    seen, out = set(), []
    for e in list(a) + list(b):
        h = e.get("entry_hash")
        if h in seen:
            continue
        seen.add(h)
        out.append(e)
    return Merged(out, sources=tuple(seen))


register("LogChain", _log_chain_merge)


# ── Cross-cutting merges ───────────────────────────────────────────
def _chaos_merge(a, b):
    fa = {f["name"]: f["prob"] for f in a.get("faults", [])}
    fb = {f["name"]: f["prob"] for f in b.get("faults", [])}
    merged = {k: max(fa.get(k, 0.0), fb.get(k, 0.0))
              for k in fa.keys() | fb.keys()}
    return Merged({"faults": [{"name": k, "prob": v}
                             for k, v in sorted(merged.items())]})


def _metric_merge(a, b):
    return Merged(_merge_dict_sum(a, b))


def _locale_merge(a, b):
    out = {**a}
    for loc, table in b.items():
        out[loc] = {**out.get(loc, {}), **table}
    return Merged(out)


def _flags_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = min(out.get(k, v), v)
    return Merged(out)


def _canary_merge(a, b):
    return Merged({
        "error_budget": min(a.get("error_budget", 1.0),
                            b.get("error_budget", 1.0)),
        "samples": a.get("samples", 0) + b.get("samples", 0),
    })


def _bucket_merge(a, b):
    return Merged({
        "tokens": min(a.get("tokens", 0.0), b.get("tokens", 0.0)),
        "burst": max(a.get("burst", 0), b.get("burst", 0)),
    })


def _circuit_merge(a, b):
    state = "OPEN" if "OPEN" in {a.get("state"), b.get("state")} else "CLOSED"
    return Merged({"state": state})


def _trace_union(a, b):
    return Merged(list(a or []) + list(b or []))


def _snapshot_merge(a, b):
    # Keep the one with a longer payload (more data preserved)
    winner = a if len(str(a.get("bytes", b""))) >= len(str(b.get("bytes", b""))) else b
    return Merged(winner, sources=(a.get("sha256", ""), b.get("sha256", "")))


register("ChaosRun", _chaos_merge)
register("MetricSeries", _metric_merge)
register("LocaleBundle", _locale_merge)
register("ContrastPair", _json_merge if False else lambda a, b: Merged(a))
register("Redaction", lambda a, b: Merged(a))
register("SemverPair", lambda a, b: Merged(a))
register("SingleFlightResult", lambda a, b: Merged(a))
register("ClockTrace", _trace_union)
register("TokenBucketState", _bucket_merge)
register("CircuitState", _circuit_merge)
register("SagaTrace", _trace_union)
register("CDCEvent", _trace_union)
register("FlagRollout", _flags_merge)
register("CanaryReport", _canary_merge)
register("BackupSnapshot", _snapshot_merge)
register("TimeSample", _trace_union)
register("DeployPlan", _flags_merge)


# ── Generic ────────────────────────────────────────────────────────
register("dict", lambda a, b: Merged(_merge_dict_last_wins(a, b)))
register("JSON", lambda a, b: Merged(_merge_dict_last_wins(a, b))
         if isinstance(a, dict) and isinstance(b, dict) else Merged(b))
register("JSONList", lambda a, b: Merged(_union_list(a, b)))
register("Dict", lambda a, b: Merged(_merge_dict_last_wins(a, b)))
register("FloatDict", lambda a, b: Merged(_merge_dict_last_wins(a, b)))
register("Bytes", lambda a, b: Merged(a if len(a) >= len(b) else b))
register("Grid", lambda a, b: Merged(a))
register("Sudoku", lambda a, b: Merged(a))
register("Crossword", lambda a, b: Merged(a))
register("Rubik", lambda a, b: Merged(a))
register("TicTacToe", lambda a, b: Merged(a))
register("GridWorld", lambda a, b: Merged(a))
register("EngineTile", lambda a, b: Merged(a))
register("EngineOutcome", lambda a, b: Merged(a))
register("Differential", lambda a, b: Merged(a))
register("DynamicController", lambda a, b: Merged(a))
register("CD", lambda a, b: Merged(a))
register("Config", lambda a, b: Merged(a))

# ── Nature phenomena ───────────────────────────────────────────────
def _nat_merge(a, b):
    """Default nature merge: keep the larger/shorter of two results."""
    if isinstance(a, dict) and isinstance(b, dict):
        # prefer non-empty, else the one with more keys
        winner = a if len(a) >= len(b) else b
        return Merged(winner, sources=())
    return Merged(a)


register("NatureResult", _nat_merge)
register("Walk", _nat_merge)
register("Flock", _nat_merge)
register("Oscillator", _nat_merge)
register("Morphogen", _nat_merge)
register("Population", _nat_merge)
register("Flow", _nat_merge)
