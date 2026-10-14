"""Auto-generated type constructor: PolicyRejectSummary."""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field, asdict


@dataclass
class PolicyRejectSummary:
    name: str
    payload: dict = field(default_factory=dict)
    ts: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def digest(self) -> str:
        canon = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canon.encode()).hexdigest()


__all__ = ["PolicyRejectSummary"]
