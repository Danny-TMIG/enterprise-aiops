"""Common shape for every proprietary object.

A proprietary object has three things:
    1.  a wire format   — the vendor's native payload/response shape
    2.  a local impl    — a real, in-process substitute
    3.  a tenant config — the identity this object pretends to be

The object is "real" if either the tenant config points at a live
endpoint or the local implementation is present and callable.
"""
from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ProprietaryObject:
    vendor: str
    env_key: str
    wire_format: str
    local_impl: Callable[..., Any] | None = None
    description: str = ""

    # ── env config ─────────────────────────────────────────────
    def tenant_endpoint(self) -> str | None:
        return os.environ.get(self.env_key)

    def has_tenant(self) -> bool:
        return bool(self.tenant_endpoint())

    def has_local(self) -> bool:
        return self.local_impl is not None

    def is_real(self) -> bool:
        return self.has_tenant() or self.has_local()

    # ── wire-format dispatch ───────────────────────────────────
    def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.has_tenant():
            return self._invoke_remote(payload)
        if self.has_local():
            return self._invoke_local(payload)
        return {"ok": False, "vendor": self.vendor,
                "reason": "no tenant, no local implementation"}

    def _invoke_remote(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Real HTTP call when a tenant URL is configured.
        try:
            import httpx
            r = httpx.post(self.tenant_endpoint(), json=payload, timeout=15.0)
            return {"ok": r.status_code < 400, "vendor": self.vendor,
                    "status": r.status_code,
                    "body": r.text[:2000], "transport": "http",
                    "ts": _now()}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "vendor": self.vendor,
                    "error": type(exc).__name__,
                    "transport": "http", "ts": _now()}

    def _invoke_local(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            t0 = time.time()
            body = self.local_impl(payload)  # type: ignore[misc]
            dt = (time.time() - t0) * 1000
            return {"ok": True, "vendor": self.vendor,
                    "body": body, "transport": "local",
                    "elapsed_ms": int(dt), "ts": _now()}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "vendor": self.vendor,
                    "error": type(exc).__name__,
                    "transport": "local", "ts": _now()}

    def to_dict(self) -> dict[str, Any]:
        return {
            "vendor": self.vendor,
            "env_key": self.env_key,
            "wire_format": self.wire_format,
            "has_tenant": self.has_tenant(),
            "has_local": self.has_local(),
            "real": self.is_real(),
            "description": self.description,
        }


class ProprietaryRuntime:
    """Container for all proprietary objects."""
    def __init__(self, objects: list[ProprietaryObject]) -> None:
        self.objects = {o.vendor: o for o in objects}

    def get(self, vendor: str) -> ProprietaryObject | None:
        return self.objects.get(vendor)

    def status(self) -> dict[str, Any]:
        return {name: o.to_dict() for name, o in self.objects.items()}

    def invoke(self, vendor: str, payload: dict[str, Any]) -> dict[str, Any]:
        o = self.get(vendor)
        if not o:
            return {"ok": False, "vendor": vendor, "reason": "unknown"}
        return o.invoke(payload)
