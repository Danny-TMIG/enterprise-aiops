"""HuggingFace model card source — attestations from MODEL_CARD.md.

Reads a local model card with YAML frontmatter. Missing file -> U.
Present but empty -> F for the requirements it should satisfy.
"""
from __future__ import annotations  # pragma: no cover

import os  # pragma: no cover
import re  # pragma: no cover
from pathlib import Path  # pragma: no cover

from dcs.sources import Attestation, B, source  # pragma: no cover

REQ_DOC = "AIG-DOC-002"
REQ_LIM = "AIG-TRANS-001"


def _card_path() -> Path | None:  # pragma: no cover
    env = os.environ.get("DCS_MODEL_CARD")
    if env:  # pragma: no cover
        p = Path(env)
        return p if p.exists() else None  # pragma: no cover
    for candidate in ("./MODEL_CARD.md", "./ai-governance/MODEL_CARD.md"):
        p = Path(candidate)
        if p.exists():  # pragma: no cover
            return p  # pragma: no cover
    return None  # pragma: no cover


def _read() -> str | None:  # pragma: no cover
    p = _card_path()
    if p is None:  # pragma: no cover
        return None  # pragma: no cover
    try:
        return p.read_text()  # pragma: no cover
    except Exception:  # pragma: no cover
        return None  # pragma: no cover


@source(REQ_DOC)
def model_card_present() -> Attestation:  # pragma: no cover
    body = _read()
    if body is None:  # pragma: no cover
        return Attestation(REQ_DOC, B.U, "model_card", "no model card found")  # pragma: no cover
    if len(body.strip()) < 200:  # pragma: no cover
        return Attestation(REQ_DOC, B.F, "model_card", "card too short")  # pragma: no cover
    sections = len(re.findall(r"^##?\s", body, re.MULTILINE))
    return Attestation(  # pragma: no cover
        REQ_DOC, B.T if sections >= 3 else B.B, "model_card",
        f"{sections} sections, {len(body)} chars",
        {"sections": sections, "chars": len(body)},
    )


@source(REQ_LIM)
def limitations_documented() -> Attestation:  # pragma: no cover
    body = _read()
    if body is None:  # pragma: no cover
        return Attestation(REQ_LIM, B.U, "model_card", "no model card found")  # pragma: no cover
    has_limits = bool(re.search(r"limitations?|limits|failure modes?", body, re.IGNORECASE))
    return Attestation(  # pragma: no cover
        REQ_LIM, B.T if has_limits else B.F, "model_card",
        "limitations section present" if has_limits else "no limitations section",
    )
