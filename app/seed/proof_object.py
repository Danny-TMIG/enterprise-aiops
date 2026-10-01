from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ProofObject:
    format: str = "proof_object_v1"
    intent: Dict[str, Any] = field(default_factory=dict)
    spec: Dict[str, Any] = field(default_factory=dict)
    artifact: Dict[str, Any] = field(default_factory=dict)
    scan: List[Dict[str, Any]] = field(default_factory=list)
    proof: List[Dict[str, Any]] = field(default_factory=list)
    kernel: Dict[str, Any] = field(default_factory=dict)
    dependency_graph: Dict[str, Any] = field(default_factory=dict)
    cpvo: Dict[str, Any] = field(default_factory=dict)
    gates: List[Dict[str, Any]] = field(default_factory=list)
    id: str = ""
    ts: str = field(default_factory=_now)
    seal: Dict[str, Any] = field(default_factory=dict)

    def compute_id(self) -> str:
        blob = json.dumps({
            "intent": self.intent.get("id"),
            "spec": self.spec.get("id"),
            "artifact": self.artifact.get("id"),
            "kernel_status": self.kernel.get("status"),
            "ts": self.ts,
        }, sort_keys=True)
        return "po-" + hashlib.sha256(blob.encode()).hexdigest()[:16]

    def finalize(self) -> "ProofObject":
        if not self.id:
            self.id = self.compute_id()
        return self

    def without_seal(self) -> Dict[str, Any]:
        return self.to_dict(include_seal=False)

    def to_dict(self, include_seal: bool = True) -> Dict[str, Any]:
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
