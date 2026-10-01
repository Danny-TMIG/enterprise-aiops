"""Shared helper for file-based sources.

Every file connector reads a JSON artifact produced by an external
tool. If the file is missing or unreadable, the source returns U.
We never invent a state.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dcs.sources import Attestation, B


def read_json(env_var: str, req_id: str, tool: str) -> tuple[dict | list | None, Attestation | None]:
    """Return (data, None) on success, or (None, U-attestation) on failure."""
    path = os.environ.get(env_var)
    if not path:
        return None, Attestation(req_id, B.U, tool, f"{env_var} not set")
    p = Path(path)
    if not p.exists():
        return None, Attestation(req_id, B.U, tool, f"{env_var}={path} not found")
    try:
        return json.loads(p.read_text()), None
    except Exception as e:
        return None, Attestation(req_id, B.U, tool,
                                 f"{path} unreadable: {type(e).__name__}: {e}")


def summarize_states(checks: list[tuple[str, B]]) -> tuple[B, list[str], list[str]]:
    """Fold a list of (name, state) into an overall state plus details.

    Returns (folded, failures, unknowns).
    """
    from dcs.sources import meet
    if not checks:
        return B.U, [], []
    folded = checks[0][1]
    failures: list[str] = []
    unknowns: list[str] = []
    for name, state in checks:
        folded = meet(folded, state)
        if state == B.F:
            failures.append(name)
        elif state == B.U:
            unknowns.append(name)
    return folded, failures, unknowns
