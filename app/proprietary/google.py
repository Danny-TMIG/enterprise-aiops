"""Google proprietary object.

Wire format: Vertex AI Agent Builder tool call (protobuf JSON).
    request:  {"tool": "verify", "parameters": {"claim": "..."}}
    response: {"fulfillmentResponse": {"messages": [...]}}
"""
from __future__ import annotations

from typing import Any

from app.proprietary.base import ProprietaryObject


def _local_verify(payload: dict[str, Any]) -> dict[str, Any]:
    params = payload.get("parameters") or payload
    claim = params.get("claim", "")
    ok = bool(claim)
    return {
        "fulfillmentResponse": {
            "messages": [{
                "text": {"text": ["PASS" if ok else "FAIL"]},
            }],
            "verdict": "PASS" if ok else "FAIL",
            "claim": claim,
            "backend": "tmig-local",
        },
    }


class GoogleObject(ProprietaryObject):
    def __init__(self) -> None:
        super().__init__(
            vendor="google",
            env_key="GOOGLE_CLOUD_PROJECT",
            wire_format="vertex-agent-builder-json",
            local_impl=_local_verify,
            description="Vertex AI Agent Builder verification backend",
        )
