"""A tiny site for grammar-derived code.

Opens are aspects of a module. Leaf kinds map to opens. Leaves
that share data have a restriction map from a bigger open to a
smaller one. The artifact exists iff the sections glue: every
restricted value is consistent with its source.

Site:

    module    covers {mod_doc, imports}
    signature covers {func_name, params, ret}
    body      covers {fbody}
    fdocs     covers {fdoc}
    tests     covers {test_name, test_body}

Restriction maps:

    body    -> signature
    fdocs   -> signature
    tests   -> signature (name only)
    module  -> (top)
    signature -> (top)

Cocycle condition:

    For any function f, every identifier referenced by f's body
    must be a parameter or a builtin.
    For every test t, every identifier referenced by t's body
    must be a function name or a builtin.
    A failure at any overlap is a non-vanishing cocycle.
"""
from __future__ import annotations

import ast
import builtins
from dataclasses import dataclass
from typing import Any

BUILTINS = set(dir(builtins)) | {
    "True", "False", "None", "self", "cls",
    "__name__", "__file__", "__doc__", "__builtins__", "__package__",
}


@dataclass(frozen=True)
class Open:
    name: str
    covers: tuple[str, ...]


SITE: dict[str, Open] = {
    "module":    Open("module",    ("mod_doc", "imports")),
    "signature": Open("signature", ("func_name", "params", "ret")),
    "body":      Open("body",      ("fbody",)),
    "fdocs":     Open("fdocs",     ("fdoc",)),
    "tests":     Open("tests",     ("test_name", "test_body")),
}

OPEN_OF_KIND: dict[str, str] = {}
for _o in SITE.values():
    for _k in _o.covers:
        OPEN_OF_KIND[_k] = _o.name

RESTRICTIONS: dict[str, list[str]] = {
    "module":    [],
    "signature": [],
    "body":      ["signature"],
    "fdocs":     ["signature"],
    "tests":     ["signature"],
}

# field lookup within a section
FIELD_OF_KIND: dict[str, str] = {
    "mod_doc":   "mod_doc",
    "imports":   "imports",
    "func_name": "name",
    "params":    "params",
    "ret":       "ret",
    "fbody":     "body",
    "fdoc":      "fdoc",
    "test_name": "name",
    "test_body": "body",
}


def restrict_to(open_name: str,
                sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return the values visible from `open_name` under its
    restriction maps. A leaf belonging to `open_name` sees exactly
    this local context and no more."""
    out: dict[str, Any] = {}
    for src in RESTRICTIONS.get(open_name, []):
        for k, v in sections.get(src, {}).items():
            if v is not None and v != "":
                out[k] = v
    return out


def add_to_section(open_name: str, kind: str, value: str,
                   sections: dict[str, dict[str, Any]]) -> None:
    field = FIELD_OF_KIND.get(kind, kind)
    sections.setdefault(open_name, {})[field] = value


def _referenced(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            out.add(node.id)
    return out


def _param_names(params: str) -> set[str]:
    try:
        tree = ast.parse(f"def _f({params}): pass")
    except SyntaxError:
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.arg):
            out.add(node.arg)
    return out


def cocycle_check(sections: dict[str, dict[str, Any]]
                  ) -> tuple[bool, list[str]]:
    violations: list[str] = []
    sig = sections.get("signature", {})
    fn_name = (sig.get("name") or "").strip()
    params = sig.get("params") or ""
    pnames = _param_names(params)

    body_sec = sections.get("body", {})
    body = body_sec.get("body") or ""
    if body:
        refs = _referenced(body)
        unknown = refs - pnames - BUILTINS
        if unknown:
            violations.append(
                f"body refs unknown: {sorted(unknown)}")

    tests_sec = sections.get("tests", {})
    tbody = tests_sec.get("body") or ""
    if tbody:
        refs = _referenced(tbody)
        allowed = BUILTINS | ({fn_name} if fn_name else set())
        unknown = refs - allowed
        if unknown:
            violations.append(
                f"tests ref {fn_name or '<no-fn>'} unknown: {sorted(unknown)}")

    return (not violations), violations


def glue(sections: dict[str, dict[str, Any]]) -> str:
    """Assemble the unique global section, given local sections."""
    dq3 = '"' * 3
    sq3 = "'" * 3
    out: list[str] = []

    mod = sections.get("module", {})
    if mod.get("mod_doc"):
        out.append(dq3 + mod["mod_doc"].strip().replace(dq3, sq3) + dq3)
        out.append("")
    if mod.get("imports"):
        out.append(mod["imports"].strip())
        out.append("")
    out.append("from __future__ import annotations")
    out.append("")

    sig = sections.get("signature", {})
    body = sections.get("body", {})
    fd = sections.get("fdocs", {})
    if sig.get("name"):
        name = sig["name"].strip().strip("`").strip(":")
        params = (sig.get("params") or "").strip()
        ret = (sig.get("ret") or "None").strip()
        out.append(f"def {name}({params}) -> {ret}:")
        if fd.get("fdoc"):
            out.append("    " + dq3 +
                       fd["fdoc"].strip().replace(dq3, sq3) + dq3)
        for ln in (body.get("body") or "pass").splitlines():
            out.append("    " + ln.lstrip())
        out.append("")

    t = sections.get("tests", {})
    if t.get("name"):
        tn = t["name"].strip().strip("`").strip(":")
        out.append(f"def {tn}() -> None:")
        for ln in (t.get("body") or "assert True").splitlines():
            out.append("    " + ln.lstrip())
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def site_summary() -> dict[str, Any]:
    return {
        "opens": sorted(SITE),
        "kinds": sorted(OPEN_OF_KIND),
        "restrictions": {k: v for k, v in RESTRICTIONS.items()},
    }
