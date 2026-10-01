"""Introspect a reference implementation and propose a standard.

Does not invent requirements. It reads an existing, hand-annotated
invariant module (``@requirement``-decorated functions) and produces a
schema-valid standard JSON.
"""

from __future__ import annotations

import importlib
import inspect
import json
from pathlib import Path
from typing import Any

MARKER = "_dcs_requirement"


def requirement(*, id: str, title: str, section: str, hats: list[str], criticality: str = "MUST"):
    """Decorator: mark a function as a standard requirement."""

    def deco(fn):
        setattr(
            fn,
            MARKER,
            {
                "id": id,
                "title": title,
                "section": section,
                "hats": hats,
                "criticality": criticality,
                "test": f"{fn.__module__}.{fn.__name__}",
            },
        )
        return fn

    return deco


def collect(module_paths: list[str]) -> list[dict[str, Any]]:
    out = []
    for mp in module_paths:
        mod = importlib.import_module(mp)
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            meta = getattr(obj, MARKER, None)
            if meta:
                out.append(meta)
    return sorted(out, key=lambda r: r["id"])


def emit(standard_meta: dict[str, Any], modules: list[str], out_path: Path) -> Path:
    doc = {"standard": standard_meta, "requirements": collect(modules)}
    out_path.write_text(json.dumps(doc, indent=2))
    return out_path


def render_markdown(doc: dict[str, Any]) -> str:
    meta = doc["standard"]
    lines = [
        f"# {meta['title']}",
        "",
        f"**Standard**: `{meta['id']}@{meta['version']}`  ",
        f"**Published**: {meta['published']}  ",
        f"**Authority**: {meta['authority']}",
        "",
        "## Requirements",
        "",
    ]
    by_section: dict[str, list[dict[str, Any]]] = {}
    for r in doc["requirements"]:
        by_section.setdefault(r["section"], []).append(r)
    for sect in sorted(by_section):
        lines.append(f"### {sect}")
        lines.append("")
        for r in by_section[sect]:
            hats = ", ".join(r["hats"])
            lines.append(f"- **{r['id']}** ({r['criticality']}) — {r['title']}")
            lines.append(f"  - hats: `{hats}`")
            lines.append(f"  - test: `{r['test']}`")
        lines.append("")
    return "\n".join(lines)
