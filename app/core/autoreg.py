"""Autoregistration. Hardcoded dicts become discovered registries."""
from __future__ import annotations

import importlib
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
APP  = ROOT / "app"

_LOCK = threading.RLock()

CAPABILITIES: dict[str, dict[str, Any]] = {}
QUERIES:      dict[str, dict[str, Callable]] = {}
TEMPLATES:    dict[str, Callable] = {}
PRIMITIVES:   dict[str, dict[str, Callable]] = {"int": {}, "list": {}, "binary": {}}
PHENOMENA:    dict[str, tuple] = {}
ECOSYSTEMS:   dict[str, dict[str, Any]] = {}
LANES:        dict[str, list[str]] = {}
MODELS:       dict[str, dict[str, Any]] = {}


def cap(code: str, *, category: str = "core", equation: str = "",
        home: str = "", status: str = "real") -> Callable:
    def deco(obj):
        with _LOCK:
            CAPABILITIES[code] = {"code": code, "category": category,
                                  "equation": equation, "home": home,
                                  "status": status, "obj": obj}
        return obj
    return deco


def query(family: str, name: str) -> Callable:
    def deco(fn):
        with _LOCK:
            QUERIES.setdefault(family, {})[name] = fn
        return fn
    return deco


def template(name: str) -> Callable:
    def deco(fn):
        with _LOCK:
            TEMPLATES[name] = fn
        return fn
    return deco


def primitive(family: str, name: str) -> Callable:
    def deco(fn):
        with _LOCK:
            PRIMITIVES.setdefault(family, {})[name] = fn
        return fn
    return deco


def phenomenon(code: str, family: str = "", rule: str = "") -> Callable:
    def deco(fn):
        with _LOCK:
            PHENOMENA[code] = (fn, family, rule)
        return fn
    return deco


def ecosystem(name: str, **fields: Any) -> Callable:
    def deco(fn):
        with _LOCK:
            ECOSYSTEMS[name] = {**fields, "_fn": fn}
        return fn
    return deco


def lane(name: str, reqs: list[str] | None = None) -> Callable:
    def deco(fn):
        with _LOCK:
            LANES[name] = list(reqs or [])
        return fn
    return deco


def model(code: str, **fields: Any) -> Callable:
    def deco(fn):
        with _LOCK:
            MODELS[code] = {**fields, "_fn": fn}
        return fn
    return deco


_SKIP = {"__pycache__", ".venv", ".lanes", ".git", "node_modules", "generated"}


def discover(*, reset: bool = False) -> dict[str, int]:
    if reset:
        with _LOCK:
            CAPABILITIES.clear(); QUERIES.clear(); TEMPLATES.clear()
            PRIMITIVES.clear(); PHENOMENA.clear(); ECOSYSTEMS.clear()
            LANES.clear(); MODELS.clear()
    n = 0
    for p in sorted(APP.rglob("*.py")):
        if any(part in _SKIP for part in p.parts):
            continue
        rel = p.relative_to(ROOT)
        mod = str(rel.with_suffix("")).replace("/", ".")
        mod = mod.removesuffix(".__init__")
        try:
            importlib.import_module(mod)
            n += 1
        except Exception:
            continue
    return snapshot()


def snapshot() -> dict[str, int]:
    with _LOCK:
        return {
            "capabilities":   len(CAPABILITIES),
            "query_families": len(QUERIES),
            "queries":        sum(len(v) for v in QUERIES.values()),
            "templates":      len(TEMPLATES),
            "primitives":     sum(len(v) for v in PRIMITIVES.values()),
            "phenomena":      len(PHENOMENA),
            "ecosystems":     len(ECOSYSTEMS),
            "lanes":          len(LANES),
            "models":         len(MODELS),
        }


def state() -> dict[str, Any]:
    with _LOCK:
        return {
            "capabilities": {k: {kk: vv for kk, vv in v.items() if kk != "obj"}
                             for k, v in CAPABILITIES.items()},
            "queries":      {f: sorted(d) for f, d in QUERIES.items()},
            "templates":    sorted(TEMPLATES),
            "primitives":   {f: sorted(d) for f, d in PRIMITIVES.items()},
            "phenomena":    {k: {"family": v[1], "rule": v[2]}
                             for k, v in PHENOMENA.items()},
            "ecosystems":   {k: {kk: vv for kk, vv in v.items() if kk != "_fn"}
                             for k, v in ECOSYSTEMS.items()},
            "lanes":        dict(LANES),
            "models":       {k: {kk: vv for kk, vv in v.items() if kk != "_fn"}
                             for k, v in MODELS.items()},
        }


def watch(callback: Callable[[dict[str, int]], None],
          *, interval: float = 2.0,
          stop: threading.Event | None = None) -> threading.Thread:
    def _run():
        last = _tree_mtime()
        while not (stop and stop.is_set()):
            time.sleep(interval)
            now = _tree_mtime()
            if now != last:
                last = now
                callback(discover())
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def _tree_mtime() -> float:
    m = 0.0
    for p in APP.rglob("*.py"):
        if any(part in _SKIP for part in p.parts):
            continue
        try:
            m = max(m, p.stat().st_mtime)
        except OSError:
            continue
    return m


__all__ = [
    "CAPABILITIES",
    "ECOSYSTEMS",
    "LANES",
    "MODELS",
    "PHENOMENA",
    "PRIMITIVES",
    "QUERIES",
    "TEMPLATES",
    "cap",
    "discover",
    "ecosystem",
    "lane",
    "model",
    "phenomenon",
    "primitive",
    "query",
    "snapshot",
    "state",
    "template",
    "watch",
]
