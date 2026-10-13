"""Sanitize leaf values from the model."""
from __future__ import annotations

import re

_ID_CHARS = re.compile(r"[^A-Za-z0-9_]")
_SIG_TAIL = re.compile(r"[\(\):=].*$", re.DOTALL)


def _strip_wrap(s: str) -> str:
    s = s.strip()
    changed = True
    while changed and len(s) >= 2:
        changed = False
        for w in ('"', "'", "`"):
            if s.startswith(w) and s.endswith(w):
                s = s[1:-1].strip()
                changed = True
    return s


def identifier(s: str) -> str:
    if not s:
        return ""
    s = _strip_wrap(s)
    s = s.splitlines()[0].strip() if s else ""
    s = _SIG_TAIL.sub("", s)
    s = _ID_CHARS.sub("_", s).strip("_")
    if not s:
        return ""
    if s[0].isdigit():
        s = "f_" + s
    return s


def test_identifier(s: str) -> str:
    s = identifier(s)
    if not s:
        return "test_ok"
    if not s.startswith("test_"):
        s = "test_" + s
    return s


def params(s: str) -> str:
    if not s:
        return ""
    s = _strip_wrap(s)
    return s.splitlines()[0].strip() if s else ""


def ret(s: str) -> str:
    s = identifier(s)
    return s or "None"


def imports(s: str) -> str:
    lines = []
    for ln in (s or "").splitlines():
        raw = ln.rstrip()
        if not raw.strip():
            continue
        if raw.strip().startswith("```"):
            continue
        lines.append(raw)
    return "\n".join(lines)


_FIELD_PREFIX = re.compile(
    r'^\s*(?:Docstring|FDoc|Fdoc|ModuleDoc|ModDoc|Doc|Text)\s*:\s*',
    re.IGNORECASE,
)


def text_field(s: str) -> str:
    if not s:
        return ""
    out = _strip_wrap(s)
    out = _FIELD_PREFIX.sub("", out).strip()
    out = _strip_wrap(out)
    return out
