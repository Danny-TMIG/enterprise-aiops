"""Frontier disintermediation.

One model (local MLX or any configured remote provider) acts as the
universal disintermediation layer. Each vendor slot is realized by a
profile: a system prompt, an output schema, and a wire mapper.

The model is asked for JSON. The JSON is parsed. The wire mapper
converts it to the vendor's native shape. If the model fails, the
call falls through to the vendor's local implementation.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.dispatch.models.base import ModelRequest
from app.dispatch.models.registry import get_registry
from app.frontier.profile import PROFILES, VendorProfile, get_profile

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    m = _JSON_BLOCK.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


@dataclass
class FrontierRequest:
    vendor: str
    intent: str
    payload: dict[str, Any] = field(default_factory=dict)
    task: str = "reasoning"
    max_tokens: int = 512
    temperature: float = 0.0


@dataclass
class FrontierResponse:
    vendor: str
    ok: bool
    wire: dict[str, Any]
    model_out: dict[str, Any]
    provider: str = ""
    model: str = ""
    dry_run: bool = False
    fallback: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "vendor": self.vendor, "ok": self.ok,
            "wire": self.wire, "model_out": self.model_out,
            "provider": self.provider, "model": self.model,
            "dry_run": self.dry_run, "fallback": self.fallback,
            "error": self.error,
        }


class FrontierDis:
    def __init__(self) -> None:
        self.registry = get_registry()
        self.profiles = PROFILES

    def profiles(self) -> dict[str, Any]:
        return {name: p.to_dict() for name, p in self.profiles.items()}

    def invoke(self, req: FrontierRequest) -> FrontierResponse:
        profile = get_profile(req.vendor)
        if profile is None:
            return FrontierResponse(
                vendor=req.vendor, ok=False, wire={}, model_out={},
                error=f"unknown vendor: {req.vendor}",
            )

        prompt = self._build_prompt(profile, req)
        model_resp = self.registry.complete(ModelRequest(
            task=req.task,
            prompt=prompt,
            system=profile.system_prompt,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            metadata={"response_format": "json"},
        ))

        model_out = _extract_json(model_resp.text) or {}
        wire = profile.to_wire(model_out, req.payload) if model_out else {}
        ok = bool(model_out) and not model_resp.dry_run

        # fallback to the local implementation if the model failed
        if not ok:
            fb = self._fallback(req.vendor, req.payload)
            if fb is not None:
                return FrontierResponse(
                    vendor=req.vendor, ok=True, wire=fb,
                    model_out=model_out,
                    provider=model_resp.provider,
                    model=model_resp.model,
                    dry_run=model_resp.dry_run,
                    fallback=True,
                )

        return FrontierResponse(
            vendor=req.vendor, ok=ok, wire=wire, model_out=model_out,
            provider=model_resp.provider, model=model_resp.model,
            dry_run=model_resp.dry_run,
        )

    def _build_prompt(self, profile: VendorProfile,
                      req: FrontierRequest) -> str:
        return (
            f"Vendor: {profile.vendor}\n"
            f"Intent: {req.intent}\n"
            f"Payload:\n{json.dumps(req.payload, indent=2, default=str)}\n\n"
            "Respond with a single JSON object matching the schema. "
            "No prose, no markdown fences."
        )

    def _fallback(self, vendor: str,
                  payload: dict[str, Any]) -> dict[str, Any] | None:
        try:
            from app.proprietary.registry import ProprietaryRegistry
            r = ProprietaryRegistry().invoke(vendor, payload)
            if r.get("ok"):
                return r.get("body") or {}
        except Exception:
            pass
        return None

    def status(self) -> dict[str, Any]:
        reg = self.registry.status()
        return {
            "profiles": list(self.profiles.keys()),
            "providers": reg["providers"],
            "local_aliases": reg["local_aliases"],
            "any_remote": reg["any_remote_available"],
            "any_local": reg["any_local_available"],
        }


_FD: FrontierDis | None = None


def get_frontier() -> FrontierDis:
    global _FD
    if _FD is None:
        _FD = FrontierDis()
    return _FD
