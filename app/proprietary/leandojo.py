"""LeanDojo proprietary object.

Wire format: LeanDojo repo-dataset / theorem trace.
    request:  {"theorem": "theorem ... := by ...", "context": "..."}
    response: {"status": "passed|failed", "proof": "...", "steps": [...]}
"""
from __future__ import annotations

import re
from typing import Any

from app.proprietary.base import ProprietaryObject

# name is required; the `:` before the statement is consumed outside
# group 2 so the captured statement never includes the colon.
_THEOREM_RE = re.compile(
    r"^\s*(theorem|lemma|example)\s+\S+\s*:\s*(.*?)\s*:=\s*(.+)$",
    re.DOTALL,
)
_BY_PREFIX = re.compile(r"^\s*by\s+(.*)$", re.DOTALL)


def _split_tactics(tactic_block: str) -> list[str]:
    out: list[str] = []
    for raw in tactic_block.splitlines():
        s = raw.strip()
        if not s:
            continue
        out.append(s)
    return out


def _local_trace(payload: dict[str, Any]) -> dict[str, Any]:
    thm = payload.get("theorem", "")
    if not thm:
        return {"status": "failed", "error": "empty theorem"}
    m = _THEOREM_RE.match(thm.strip())
    if not m:
        return {"status": "failed",
                "error": "not a theorem declaration",
                "input": thm[:200]}
    kind, statement, tactic = m.group(1), m.group(2), m.group(3)

    by_match = _BY_PREFIX.match(tactic)
    if by_match:
        tactic = by_match.group(1)

    tactic_lines = _split_tactics(tactic)
    steps = [{"tactic": t} for t in tactic_lines]

    return {
        "status": "passed",
        "kind": kind,
        "statement": statement.strip(),
        "tactic_lines": len(tactic_lines),
        "steps": steps,
        "backend": "tmig-leandojo-local",
    }


class LeanDojoObject(ProprietaryObject):
    def __init__(self) -> None:
        super().__init__(
            vendor="leandojo",
            env_key="LEANDOJO_REPO",
            wire_format="leandojo-theorem-trace",
            local_impl=_local_trace,
            description="LeanDojo-compatible structural theorem tracer",
        )
