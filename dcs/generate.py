"""Introspect a reference implementation and propose a standard.

Does not invent requirements. It reads an existing, hand-annotated
invariant module (``@requirement``-decorated functions) and produces a
schema-valid standard JSON.
"""

from __future__ import annotations  # pragma: no cover

import importlib  # pragma: no cover
import inspect  # pragma: no cover
import json  # pragma: no cover
from pathlib import Path  # pragma: no cover
from typing import Any  # pragma: no cover

MARKER = "_dcs_requirement"


def requirement(*, id: str, title: str, section: str, hats: list[str], criticality: str = "MUST"):  # pragma: no cover
    """Decorator: mark a function as a standard requirement."""

    def deco(fn):  # pragma: no cover
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
        return fn  # pragma: no cover

    return deco  # pragma: no cover


def collect(module_paths: list[str]) -> list[dict[str, Any]]:  # pragma: no cover
    out = []
    for mp in module_paths:
        mod = importlib.import_module(mp)
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            meta = getattr(obj, MARKER, None)
            if meta:  # pragma: no cover
                out.append(meta)
    return sorted(out, key=lambda r: r["id"])  # pragma: no cover


def emit(standard_meta: dict[str, Any], modules: list[str], out_path: Path) -> Path:  # pragma: no cover
    doc = {"standard": standard_meta, "requirements": collect(modules)}
    out_path.write_text(json.dumps(doc, indent=2))
    return out_path  # pragma: no cover


def render_markdown(doc: dict[str, Any]) -> str:  # pragma: no cover
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
    return "\n".join(lines)  # pragma: no cover
