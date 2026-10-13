"""Coalescence — canonical form for every leaf value.

Two texts are equivalent iff their canonical forms are equal.
The canonical form for a code block is the output of
`ast.unparse` after dedent+parse. This wipes fences, indentation,
backticks, and wrapper prefixes in one step.

Nothing downstream ever sees the raw text.
"""
from __future__ import annotations

import ast
import re
from typing import Any

_FENCE_RE = re.compile(r"```[a-zA-Z]*\s*\n?(.*?)```", re.DOTALL)
_WRAP = ('"', "'", "`")
_FIELD_PREFIX = re.compile(
    r"^\s*(?:Docstring|FDoc|ModuleDoc|ModDoc|Doc|Text|Params|Ret|Name)"
    r"\s*[:=]\s*",
    re.IGNORECASE,
)
_ID_TAIL = re.compile(r"[\(\):=\s].*$", re.DOTALL)


def _strip_wrap(s: str) -> str:
    s = s.strip()
    changed = True
    while changed and len(s) >= 2:
        changed = False
        for w in _WRAP:
            if s.startswith(w) and s.endswith(w):
                s = s[1:-1].strip()
                changed = True
    return s


def _strip_fences(s: str) -> str:
    m = _FENCE_RE.search(s)
    if m:
        s = m.group(1)
    kept = [ln for ln in s.splitlines() if not ln.strip().startswith("```")]
    return "\n".join(kept)


def _dedent(text: str) -> str:
    lines = text.splitlines()
    indents = [len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()]
    cut = min(indents) if indents else 0
    return "\n".join(ln[cut:] if len(ln) >= cut else ln.lstrip()
                     for ln in lines)


def _try_parse_module(text: str) -> str:
    """Return unparsed module source, or the dedented text if that
    fails."""
    try:
        tree = ast.parse(text)
        return ast.unparse(tree)
    except SyntaxError:
        pass
    # tolerate a bare block: wrap in `if True:` then unparse
    try:
        wrapped = "if True:\n" + "\n".join(
            ("    " + ln) if ln.strip() else ln
            for ln in text.splitlines())
        tree = ast.parse(wrapped)
        inner = tree.body[0].body
        return "\n".join(ast.unparse(stmt) for stmt in inner)
    except SyntaxError:
        return text


# ── public canonicalizers ────────────────────────────────────
def canonical_identifier(s: str) -> str:
    if not s:
        return ""
    s = _strip_wrap(s)
    s = _FIELD_PREFIX.sub("", s)
    s = s.splitlines()[0].strip() if s else ""
    s = _ID_TAIL.sub("", s)
    s = re.sub(r"[^A-Za-z0-9_]", "_", s).strip("_")
    if not s:
        return ""
    if s[0].isdigit():
        s = "f_" + s
    return s


def canonical_test_identifier(s: str) -> str:
    s = canonical_identifier(s)
    if not s:
        return "test_ok"
    if not s.startswith("test_"):
        s = "test_" + s
    return s


def canonical_params(s: str) -> str:
    if not s:
        return ""
    s = _strip_wrap(s)
    s = _FIELD_PREFIX.sub("", s)
    # a param list like `x: int, y: str` — keep the interior
    try:
        tree = ast.parse(f"def _f({s}): pass")
        fn = tree.body[0]
        parts = []
        for a in fn.args.args:
            if a.annotation is not None:
                parts.append(f"{a.arg}: {ast.unparse(a.annotation)}")
            else:
                parts.append(a.arg)
        return ", ".join(parts)
    except SyntaxError:
        return s.splitlines()[0].strip() if s else ""


def canonical_ret(s: str) -> str:
    s = canonical_identifier(s)
    return s or "None"


def canonical_imports(s: str) -> str:
    if not s:
        return ""
    s = _strip_fences(s)
    s = _dedent(s)
    try:
        tree = ast.parse(s)
    except SyntaxError:
        # keep only lines that look like imports
        kept = [ln for ln in s.splitlines()
                if ln.strip().startswith(("import ", "from "))]
        return "\n".join(kept)
    kept = [n for n in tree.body
            if isinstance(n, (ast.Import, ast.ImportFrom))]
    return "\n".join(ast.unparse(n) for n in kept)


def canonical_body(s: str) -> str:
    """Return a canonical, dedented block at column 0 with internal
    indentation intact."""
    if not s or not s.strip():
        return "pass"
    s = _strip_fences(s)
    s = _dedent(s)
    s = _try_parse_module(s)
    return s or "pass"


def canonical_text(s: str) -> str:
    if not s:
        return ""
    s = _strip_wrap(s)
    s = _FIELD_PREFIX.sub("", s)
    return _strip_wrap(s).strip()


def indent(block: str, spaces: int = 4) -> list[str]:
    """Indent every non-empty line of a canonical block."""
    pad = " " * spaces
    return [(pad + ln) if ln.strip() else "" for ln in block.splitlines()]


# ── equivalence ───────────────────────────────────────────────
def key(kind: str, value: str) -> tuple[str, Any]:
    if kind in ("func_name", "test_name", "ret"):
        return (kind, canonical_identifier(value))
    if kind == "params":
        return ("params", canonical_params(value))
    if kind == "imports":
        return ("imports", canonical_imports(value))
    if kind in ("fbody", "test_body"):
        return ("code", canonical_body(value))
    return ("text", canonical_text(value))


def equivalent(kind: str, a: str, b: str) -> bool:
    return key(kind, a) == key(kind, b)


# ── short aliases (callers don't need the long names) ────────
identifier = canonical_identifier
test_identifier = canonical_test_identifier
params = canonical_params
ret = canonical_ret
imports = canonical_imports
body = canonical_body
text = canonical_text


# ── short aliases (callers don't need the long names) ────────
identifier = canonical_identifier
test_identifier = canonical_test_identifier
params = canonical_params
ret = canonical_ret
imports = canonical_imports
body = canonical_body
text = canonical_text
