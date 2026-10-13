"""Salesforce proprietary object.

Wire format: Apex callout / Agentforce external service.
    request:  {"action": "verify", "claim": "...", "context": {...}}
    response: {"success": bool, "data": {...}, "errors": [...]}
"""
from __future__ import annotations

from typing import Any

from app.proprietary.base import ProprietaryObject


def _local_verify(payload: dict[str, Any]) -> dict[str, Any]:
    claim = payload.get("claim", "")
    ctx = payload.get("context") or {}
    ok = bool(claim)
    return {
        "success": ok,
        "data": {
            "verdict": "PASS" if ok else "FAIL",
            "claim": claim,
            "context_keys": sorted(ctx.keys()),
        },
        "errors": [] if ok else [{"code": "EMPTY_CLAIM"}],
    }


class SalesforceObject(ProprietaryObject):
    def __init__(self) -> None:
        super().__init__(
            vendor="salesforce",
            env_key="SALESFORCE_ORG_URL",
            wire_format="apex-callout-json",
            local_impl=_local_verify,
            description="Agentforce / Apex verification backend",
        )
