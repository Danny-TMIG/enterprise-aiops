"""Microsoft proprietary object.

Wire format: Power Automate HTTP trigger / Copilot Studio action.
    request:  {"type": "verify", "claim": "...", "evidence": [...]}
    response: {"status": "succeeded|failed", "outputs": {...}}
"""
from __future__ import annotations

from typing import Any

from app.proprietary.base import ProprietaryObject


def _local_verify(payload: dict[str, Any]) -> dict[str, Any]:
    claim = payload.get("claim", "")
    evidence = payload.get("evidence") or []
    ok = bool(claim) and isinstance(evidence, list)
    return {
        "status": "succeeded" if ok else "failed",
        "outputs": {
            "verdict": "PASS" if ok else "FAIL",
            "claim": claim,
            "evidence_count": len(evidence),
            "backend": "tmig-local",
        },
    }


class MicrosoftObject(ProprietaryObject):
    def __init__(self) -> None:
        super().__init__(
            vendor="microsoft",
            env_key="MICROSOFT_VERIFY_ENDPOINT",
            wire_format="power-automate-http-trigger",
            local_impl=_local_verify,
            description="Power Automate / Copilot Studio verification backend",
        )
