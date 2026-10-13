"""ServiceNow proprietary object.

Wire format: Flow Designer REST action.
    request:  {"action": "verify", "inputs": {"claim": "..."}}
    response: {"result": {"state": "success|error", "output": {...}}}
"""
from __future__ import annotations

from typing import Any

from app.proprietary.base import ProprietaryObject


def _local_verify(payload: dict[str, Any]) -> dict[str, Any]:
    inputs = payload.get("inputs") or payload
    claim = inputs.get("claim", "")
    ok = bool(claim)
    return {
        "result": {
            "state": "success" if ok else "error",
            "output": {
                "verdict": "PASS" if ok else "FAIL",
                "claim": claim,
                "backend": "tmig-local",
            },
        },
    }


class ServiceNowObject(ProprietaryObject):
    def __init__(self) -> None:
        super().__init__(
            vendor="servicenow",
            env_key="SERVICENOW_INSTANCE",
            wire_format="flow-designer-rest",
            local_impl=_local_verify,
            description="Now Assist / Flow Designer verification backend",
        )
