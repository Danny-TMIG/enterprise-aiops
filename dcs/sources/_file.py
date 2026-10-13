"""Shared helper for file-based sources.

Every file connector reads a JSON artifact produced by an external
tool. If the file is missing or unreadable, the source returns U.
We never invent a state.
"""

from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
import os  # pragma: no cover
from pathlib import Path  # pragma: no cover

from dcs.sources import Attestation, B  # pragma: no cover


def read_json(  # pragma: no cover
    env_var: str, req_id: str, tool: str
) -> tuple[dict | list | None, Attestation | None]:
    """Return (data, None) on success, or (None, U-attestation) on failure."""
    path = os.environ.get(env_var)
    if not path:  # pragma: no cover
        return None, Attestation(req_id, B.U, tool, f"{env_var} not set")  # pragma: no cover
    p = Path(path)
    if not p.exists():  # pragma: no cover
        return None, Attestation(req_id, B.U, tool, f"{env_var}={path} not found")  # pragma: no cover
    try:
        return json.loads(p.read_text()), None  # pragma: no cover
    except Exception as e:  # pragma: no cover
        return None, Attestation(req_id, B.U, tool, f"{path} unreadable: {type(e).__name__}: {e}")  # pragma: no cover


def summarize_states(checks: list[tuple[str, B]]) -> tuple[B, list[str], list[str]]:  # pragma: no cover
    """Fold a list of (name, state) into an overall state plus details.

    Returns (folded, failures, unknowns).
    """
    from dcs.sources import meet  # pragma: no cover

    if not checks:  # pragma: no cover
        return B.U, [], []  # pragma: no cover
    folded = checks[0][1]
    failures: list[str] = []
    unknowns: list[str] = []
    for name, state in checks:
        folded = meet(folded, state)
        if state == B.F:  # pragma: no cover
            failures.append(name)
        elif state == B.U:
            unknowns.append(name)
    return folded, failures, unknowns  # pragma: no cover
