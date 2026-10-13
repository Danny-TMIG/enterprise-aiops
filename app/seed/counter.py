"""Seal counter.

V is a system measurement, not a grep.

    V = verified_seals / emitted_proof_objects

Persists to data/moat_seal_counter.json so it survives restarts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_COUNTER_PATH = Path("./data/moat_seal_counter.json")
_DEFAULT: dict[str, int] = {"emitted": 0, "sealed": 0, "verified": 0}


def _load() -> dict[str, int]:
    if _COUNTER_PATH.exists():
        try:
            d = json.loads(_COUNTER_PATH.read_text())
            return {
                "emitted": int(d.get("emitted", 0)),
                "sealed": int(d.get("sealed", 0)),
                "verified": int(d.get("verified", 0)),
            }
        except Exception:
            pass
    return dict(_DEFAULT)


def _save(d: dict[str, int]) -> None:
    _COUNTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    _COUNTER_PATH.write_text(json.dumps(d, indent=2))


def record_emit(proof_object: dict[str, Any]) -> dict[str, int]:
    d = _load()
    d["emitted"] += 1
    seal = (proof_object or {}).get("seal") or {}
    if seal.get("signatures"):
        d["sealed"] += 1
        try:
            from app.seed.seal import verify_seal
            if verify_seal(seal):
                d["verified"] += 1
        except Exception:
            pass
    _save(d)
    return d


def stats() -> dict[str, Any]:
    d = _load()
    v = (d["verified"] / d["emitted"]) if d["emitted"] else 0.0
    return {**d, "v": round(v, 6)}


def reset() -> None:
    _save(dict(_DEFAULT))
