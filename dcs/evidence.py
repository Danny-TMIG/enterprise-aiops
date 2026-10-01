"""Content-addressed + optionally signed evidence bundle."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import nacl.signing  # type: ignore

    _NACL = True
except Exception:
    _NACL = False


def canonical(obj: Any) -> bytes:
    """Deterministic JSON for hashing/signing (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def digest_of(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


@dataclass
class RequirementResult:
    id: str
    criticality: str
    pass_: bool
    duration_ms: float
    detail: str = ""
    evidence: str = ""  # sha256 of the detail blob
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["pass"] = d.pop("pass_")
        return d


@dataclass
class Bundle:
    standard_ref: str
    reference: dict[str, Any]
    started: float
    completed: float
    results: list[RequirementResult] = field(default_factory=list)
    signature: str | None = None
    public_key: str | None = None
    digest: str | None = None

    def seal(self) -> Bundle:
        self.digest = digest_of(self._unsigned())
        return self

    def sign(self, key_path: Path | None = None) -> Bundle:
        if not _NACL:
            return self
        if key_path and key_path.exists():
            key = nacl.signing.SigningKey(bytes.fromhex(key_path.read_text().strip()))
        else:
            key = nacl.signing.SigningKey.generate()
        payload = canonical(self._unsigned())
        sig = key.sign(payload).signature
        self.signature = sig.hex()
        self.public_key = key.verify_key.encode().hex()
        return self

    def _unsigned(self) -> dict[str, Any]:
        return {
            "standard_ref": self.standard_ref,
            "reference": self.reference,
            "started": self.started,
            "completed": self.completed,
            "results": [r.to_dict() for r in self.results],
        }

    def summary(self) -> dict[str, int]:
        s = {
            "MUST_pass": 0,
            "MUST_fail": 0,
            "SHOULD_pass": 0,
            "SHOULD_fail": 0,
            "MAY_pass": 0,
            "MAY_fail": 0,
        }
        for r in self.results:
            s[f"{r.criticality}_{'pass' if r.pass_ else 'fail'}"] += 1
        return s

    def verdict(self) -> str:
        if any(r.criticality == "MUST" and not r.pass_ for r in self.results):
            return "NON_CONFORMANT"
        return "CONFORMANT"

    def to_dict(self) -> dict[str, Any]:
        d = self._unsigned()
        d["summary"] = self.summary()
        d["verdict"] = self.verdict()
        d["digest"] = self.digest
        d["signature"] = self.signature
        d["public_key"] = self.public_key
        return d

    def write(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str))
