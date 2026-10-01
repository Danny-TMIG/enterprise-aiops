"""Equivalence relations project-wide.

Two flavors per artifact kind:

    EXACT     — content-addressed. Bytewise identical.
    SEMANTIC  — behaviorally interchangeable. Ignores volatile fields.

Rules:
    reflexive, symmetric, transitive for both.
    exact ⇒ semantic (checked by DCS-EQ-002).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Dict, Iterable, Tuple


ExactFn = Callable[[Any, Any], bool]
SemanticFn = Callable[[Any, Any], bool]
_REGISTRY: Dict[str, Tuple[ExactFn, SemanticFn]] = {}


def register(kind: str, exact: ExactFn, semantic: SemanticFn) -> None:
    _REGISTRY[kind] = (exact, semantic)


def exact(kind: str, a: Any, b: Any) -> bool:
    if kind not in _REGISTRY:
        raise KeyError(f"no equivalence relation for {kind!r}")
    return _REGISTRY[kind][0](a, b)


def semantic(kind: str, a: Any, b: Any) -> bool:
    if kind not in _REGISTRY:
        raise KeyError(f"no equivalence relation for {kind!r}")
    return _REGISTRY[kind][1](a, b)


def relation_for(kind: str):
    return _REGISTRY[kind]


def kinds() -> list[str]:
    return sorted(_REGISTRY.keys())


# ── helpers ─────────────────────────────────────────────────────────
def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def _digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(_canon(obj)).hexdigest()


def _proj(d: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    return {k: d.get(k) for k in keys}


def _json_exact(a, b) -> bool:
    return _canon(a) == _canon(b)


def _json_semantic(a, b) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        keys = sorted(set(a) | set(b))
        return _proj(a, keys) == _proj(b, keys)
    return a == b


def _digest_exact(a, b) -> bool:
    da = getattr(a, "digest", None) or str(a)
    db = getattr(b, "digest", None) or str(b)
    return da == db


def _digest_only_semantic(a, b) -> bool:
    return _digest_exact(a, b)


def _float_close(x: float, y: float, tol: float = 1e-12) -> bool:
    return abs(x - y) < tol


def _dict_close(a: dict, b: dict) -> bool:
    if set(a) != set(b):
        return False
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, float) and isinstance(vb, float):
            if not _float_close(va, vb):
                return False
        elif va != vb:
            return False
    return True


# ── domain-specific registrations ──────────────────────────────────

# dict / JSON — base
register("dict", _json_exact, _json_semantic)
register("JSON", _json_exact, _json_semantic)
register("JSONList", _json_exact, _json_semantic)


# TrainTile
def _tile_exact(a, b):
    return a.to_dict() == b.to_dict()


def _tile_semantic(a, b):
    return (a.kind, a.solver, a.difficulty, a.trials, a.passes) == \
           (b.kind, b.solver, b.difficulty, b.trials, b.passes)


register("TrainTile", _tile_exact, _tile_semantic)


def _tile_list_exact(a, b):
    return [t.to_dict() for t in a] == [t.to_dict() for t in b]


def _tile_list_semantic(a, b):
    ka = sorted((t.kind, t.solver, t.difficulty, t.trials, t.passes) for t in a)
    kb = sorted((t.kind, t.solver, t.difficulty, t.trials, t.passes) for t in b)
    return ka == kb


register("TileList", _tile_list_exact, _tile_list_semantic)


# TrainOutcome
register("TrainOutcome", _digest_exact, _digest_only_semantic)


def _outcome_list_exact(a, b):
    return [o.digest for o in a] == [o.digest for o in b]


def _outcome_list_semantic(a, b):
    return sorted(o.digest for o in a) == sorted(o.digest for o in b)


register("OutcomeList", _outcome_list_exact, _outcome_list_semantic)


# Run
def _run_exact(a, b):
    return a.digest == b.digest


def _run_semantic(a, b):
    return _dict_close(a.rates, b.rates)


register("Run", _run_exact, _run_semantic)


def _runs_exact(a, b):
    return [r.digest for r in a] == [r.digest for r in b]


def _runs_semantic(a, b):
    if len(a) != len(b):
        return False
    return all(_run_semantic(x, y) for x, y in zip(a, b))


register("RunSequence", _runs_exact, _runs_semantic)


# MeshOfMeshes
def _mesh_exact(a, b):
    return [r.digest for r in a.runs] == [r.digest for r in b.runs]


def _mesh_semantic(a, b):
    return sorted(r.digest for r in a.runs) == sorted(r.digest for r in b.runs)


register("MeshOfMeshes", _mesh_exact, _mesh_semantic)


# Weave
def _weave_exact(a, b):
    return _canon(a) == _canon(b)


def _weave_semantic(a, b):
    return (a.get("runs") == b.get("runs")
            and a.get("outcomes") == b.get("outcomes"))


register("Weave", _weave_exact, _weave_semantic)


# CrissCross
def _cc_exact(a, b):
    return _canon(a) == _canon(b)


def _cc_semantic(a, b):
    return a.get("combined") == b.get("combined")


register("CrissCross", _cc_exact, _cc_semantic)


# Pollinate
def _pl_exact(a, b):
    return a == b


def _pl_semantic(a, b):
    key = lambda p: (p["stream"], p["change"])
    return sorted(map(key, a)) == sorted(map(key, b))


register("Pollinate", _pl_exact, _pl_semantic)


# Standard / Requirement
def _req_exact(a, b):
    return (a.id, a.title, a.section, tuple(a.hats),
            a.criticality, a.test) == \
           (b.id, b.title, b.section, tuple(b.hats),
            b.criticality, b.test)


def _req_semantic(a, b):
    return a.id == b.id


register("Requirement", _req_exact, _req_semantic)


def _std_exact(a, b):
    return a.ref == b.ref and \
        [(r.id, r.test) for r in a.requirements] == \
        [(r.id, r.test) for r in b.requirements]


def _std_semantic(a, b):
    return sorted((r.id, r.criticality) for r in a.requirements) == \
           sorted((r.id, r.criticality) for r in b.requirements)


register("Standard", _std_exact, _std_semantic)


# Evidence Bundle
def _bundle_exact(a, b):
    return a.get("digest") == b.get("digest")


def _bundle_semantic(a, b):
    if a.get("standard_ref") != b.get("standard_ref"):
        return False
    if a.get("verdict") != b.get("verdict"):
        return False
    key = lambda r: (r["id"], bool(r.get("pass")))
    return sorted(map(key, a.get("results", []))) == \
           sorted(map(key, b.get("results", [])))


register("Bundle", _bundle_exact, _bundle_semantic)


# LogEntry
def _log_exact(a, b):
    return a.get("entry_hash") == b.get("entry_hash")


def _log_semantic(a, b):
    return (a.get("bundle") == b.get("bundle")
            and a.get("verdict") == b.get("verdict"))


register("LogEntry", _log_exact, _log_semantic)


# Log chain
def _chain_exact(a, b):
    return [e.get("entry_hash") for e in a] == \
           [e.get("entry_hash") for e in b]


def _chain_semantic(a, b):
    return [e.get("bundle") for e in a] == [e.get("bundle") for e in b]


register("LogChain", _chain_exact, _chain_semantic)


# Cross-cutting
register("ChaosRun", _json_exact, _json_semantic)
register("MetricSeries", _json_exact, _json_semantic)
register("LocaleBundle", _json_exact, _json_semantic)
register("ContrastPair", _json_exact, _json_semantic)
register("Redaction", _json_exact, _json_semantic)
register("SemverPair", _json_exact, _json_semantic)
register("SingleFlightResult", _json_exact, _json_semantic)
register("ClockTrace", _json_exact, _json_semantic)
register("TokenBucketState", _json_exact, _json_semantic)
register("CircuitState", _json_exact, _json_semantic)
register("SagaTrace", _json_exact, _json_semantic)
register("CDCEvent", _json_exact, _json_semantic)
register("FlagRollout", _json_exact, _json_semantic)
register("CanaryReport", _json_exact, _json_semantic)
register("BackupSnapshot", _json_exact, _json_semantic)
register("TimeSample", _json_exact, _json_semantic)
register("DeployPlan", _json_exact, _json_semantic)


# Puzzle artifacts
def _grid_exact(a, b):
    return _canon(a) == _canon(b)


def _grid_semantic(a, b):
    return a == b


for kind in ("Grid", "Sudoku", "Crossword", "Rubik", "TicTacToe", "GridWorld"):
    register(kind, _grid_exact, _grid_semantic)


# Engine artifacts
for kind in ("EngineTile", "EngineOutcome", "Differential", "DynamicController"):
    register(kind, _digest_exact, _digest_only_semantic)


# CD / NAND
def _cd_exact(a, b):
    return repr(a) == repr(b)


def _cd_semantic(a, b):
    return repr(a) == repr(b)


register("CD", _cd_exact, _cd_semantic)


# Configs
def _config_exact(a, b):
    return _canon(a.to_dict() if hasattr(a, "to_dict") else a.__dict__) == \
           _canon(b.to_dict() if hasattr(b, "to_dict") else b.__dict__)


def _config_semantic(a, b):
    da = a.to_dict() if hasattr(a, "to_dict") else a.__dict__
    db = b.to_dict() if hasattr(b, "to_dict") else b.__dict__
    da = {k: v for k, v in da.items() if not k.startswith("_")}
    db = {k: v for k, v in db.items() if not k.startswith("_")}
    return da == db


register("Config", _config_exact, _config_semantic)


# Generic dict of dicts (for rates, metrics)
register("Dict", _json_exact, _json_semantic)
register("FloatDict", _json_exact, lambda a, b: _dict_close(a, b) if
         isinstance(a, dict) and isinstance(b, dict) else a == b)


# Byte blobs
def _bytes_exact(a, b):
    return a == b


def _bytes_semantic(a, b):
    return a == b


register("Bytes", _bytes_exact, _bytes_semantic)


# ── canonical key ──────────────────────────────────────────────────
def canonical_key(kind: str, obj: Any) -> str:
    if hasattr(obj, "digest"):
        return getattr(obj, "digest")
    if kind == "TrainTile":
        return f"{obj.kind}/{obj.solver}/{obj.difficulty}"
    if kind == "Bundle":
        return obj.get("digest") or _digest(obj)
    return _digest(obj)

# ── Nature phenomena ───────────────────────────────────────────────
def _nat_exact(a, b):
    return _canon(a) == _canon(b)


def _nat_semantic(a, b):
    """Two nature results are interchangeable if their named
    summary fields match within float tolerance; the full grid/state
    is present but not compared (expensive, and layout is often not
    semantically meaningful)."""
    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a) & set(b)
        ignore = {"a", "b", "u", "v", "pos", "vel", "grid", "dirs"}
        for k in keys - ignore:
            va, vb = a[k], b[k]
            if isinstance(va, float) and isinstance(vb, float):
                if abs(va - vb) > 1e-6:
                    return False
            elif va != vb:
                return False
        return True
    return a == b


register("NatureResult", _nat_exact, _nat_semantic)
register("Walk", _nat_exact, _nat_semantic)
register("Flock", _nat_exact, _nat_semantic)
register("Oscillator", _nat_exact, _nat_semantic)
register("Morphogen", _nat_exact, _nat_semantic)
register("Population", _nat_exact, _nat_semantic)
register("Flow", _nat_exact, _nat_semantic)
