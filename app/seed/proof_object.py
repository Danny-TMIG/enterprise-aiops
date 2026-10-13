from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ProofObject:
    format: str = "proof_object_v1"
    intent: dict[str, Any] = field(default_factory=dict)
    spec: dict[str, Any] = field(default_factory=dict)
    artifact: dict[str, Any] = field(default_factory=dict)
    scan: list[dict[str, Any]] = field(default_factory=list)
    proof: list[dict[str, Any]] = field(default_factory=list)
    kernel: dict[str, Any] = field(default_factory=dict)
    dependency_graph: dict[str, Any] = field(default_factory=dict)
    cpvo: dict[str, Any] = field(default_factory=dict)
    gates: list[dict[str, Any]] = field(default_factory=list)
    id: str = ""
    ts: str = field(default_factory=_now)
    seal: dict[str, Any] = field(default_factory=dict)

    def compute_id(self) -> str:
        blob = json.dumps({
            "intent": self.intent.get("id"),
            "spec": self.spec.get("id"),
            "artifact": self.artifact.get("id"),
            "kernel_status": self.kernel.get("status"),
            "ts": self.ts,
        }, sort_keys=True)
        return "po-" + hashlib.sha256(blob.encode()).hexdigest()[:16]

    def finalize(self) -> ProofObject:
        if not self.id:
            self.id = self.compute_id()
        return self

    def without_seal(self) -> dict[str, Any]:
        return self.to_dict(include_seal=False)

    def to_dict(self, include_seal: bool = True) -> dict[str, Any]:
        d = {
            "format": self.format, "id": self.id, "ts": self.ts,
            "intent": self.intent, "spec": self.spec,
            "artifact": self.artifact,
            "scan": self.scan, "proof": self.proof,
            "kernel": self.kernel,
            "dependency_graph": self.dependency_graph,
            "cpvo": self.cpvo, "gates": self.gates,
        }
        if include_seal:
            d["seal"] = self.seal
        return d
