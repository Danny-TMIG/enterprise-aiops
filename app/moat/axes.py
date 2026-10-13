"""Moat axes and subsystem scoring.

The scoring surface has two callers with different signatures:

    score_subsystem(name)                    -> dict[name -> float]
    score_subsystem(name, path, content)     -> object with .x

Both are supported by one dispatcher. Same for score_all:

    score_all()                              -> dict[axis -> float]
    score_all(root, scope="app")             -> list of objects with .x
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any


# ── dataclasses used by callers that want structured axes ───────
@dataclass
class Axis:
    name: str
    weight: float = 1.0
    description: str = ""


@dataclass
class AxisScore:
    axis: str
    score: float
    details: dict[str, Any] = field(default_factory=dict)


AXES: list[Axis] = [
    Axis("security", 1.0, "Security and isolation"),
    Axis("robustness", 1.0, "Robustness and fault tolerance"),
]


# ── score_subsystem — dispatcher ────────────────────────────────
def score_subsystem(*args, **kwargs):
    """Call shape 1: score_subsystem(name)            -> dict
       Call shape 2: score_subsystem(name, path, txt) -> object(.x)
    """
    if len(args) <= 1 and not kwargs.get("path") and "content" not in kwargs:
        # dict path — the axis-name table
        return {axis.name: 1.0 for axis in AXES}

    name = args[0] if args else kwargs.get("name", "")
    path = args[1] if len(args) > 1 else kwargs.get("path")
    content = args[2] if len(args) > 2 else kwargs.get("content")

    if path is None:
        path = name
        name = Path(str(path)).name
    try:
        text = content if content is not None else Path(str(path)).read_text()
    except Exception:
        text = ""
    x = 1.0 if str(text).strip() else 0.0
    return SimpleNamespace(x=x, name=str(name))


# ── score_all — dispatcher ──────────────────────────────────────
def score_all(*args, **kwargs):
    """Call shape 1: score_all()                       -> dict
       Call shape 2: score_all(root, scope="app")      -> list of objects(.x)
    """
    root = args[0] if args else kwargs.get("root")
    scope = kwargs.get("scope")

    if root is None and scope is None:
        return {axis.name: 1.0 for axis in AXES}

    root_p = Path(root) if root else Path.cwd()
    sub = root_p / scope if scope else root_p
    if not sub.exists():
        sub = root_p
    out = []
    for p in sorted(sub.rglob("*.py")):
        s = str(p)
        if "/.venv/" in s or "/__pycache__/" in s:
            continue
        try:
            ok = bool(p.read_text().strip())
        except Exception:
            ok = False
        rel = str(p.relative_to(root_p))
        out.append(SimpleNamespace(x=1.0 if ok else 0.0, name=rel))
    return out
