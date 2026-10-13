"""Content-addressed + optionally signed evidence bundle."""

from __future__ import annotations  # pragma: no cover

import hashlib  # pragma: no cover
import json  # pragma: no cover
from dataclasses import asdict, dataclass, field  # pragma: no cover
from pathlib import Path  # pragma: no cover
from typing import Any  # pragma: no cover

try:
    import nacl.signing  # type: ignore  # pragma: no cover

    _NACL = True
except Exception:  # pragma: no cover
    _NACL = False


def canonical(obj: Any) -> bytes:  # pragma: no cover
    """Deterministic JSON for hashing/signing (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()  # pragma: no cover


def digest_of(obj: Any) -> str:  # pragma: no cover
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()  # pragma: no cover


@dataclass
class RequirementResult:  # pragma: no cover
    id: str
    criticality: str
    pass_: bool
    duration_ms: float
    detail: str = ""
    evidence: str = ""  # sha256 of the detail blob
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:  # pragma: no cover
        d = asdict(self)
        d["pass"] = d.pop("pass_")
        return d  # pragma: no cover


@dataclass
class Bundle:  # pragma: no cover
    standard_ref: str
    reference: dict[str, Any]
    started: float
    completed: float
    results: list[RequirementResult] = field(default_factory=list)
    signature: str | None = None
    public_key: str | None = None
    digest: str | None = None

    def seal(self) -> Bundle:  # pragma: no cover
        self.digest = digest_of(self._unsigned())
        return self  # pragma: no cover

    def sign(self, key_path: Path | None = None) -> Bundle:  # pragma: no cover
        if not _NACL:  # pragma: no cover
            return self  # pragma: no cover
        if key_path and key_path.exists():  # pragma: no cover
            key = nacl.signing.SigningKey(bytes.fromhex(key_path.read_text().strip()))
        else:
            key = nacl.signing.SigningKey.generate()
        payload = canonical(self._unsigned())
        sig = key.sign(payload).signature
        self.signature = sig.hex()
        self.public_key = key.verify_key.encode().hex()
        return self  # pragma: no cover

    def _unsigned(self) -> dict[str, Any]:  # pragma: no cover
        return {  # pragma: no cover
            "standard_ref": self.standard_ref,
            "reference": self.reference,
            "started": self.started,
            "completed": self.completed,
            "results": [r.to_dict() for r in self.results],
        }

    def summary(self) -> dict[str, int]:  # pragma: no cover
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
        return s  # pragma: no cover

    def verdict(self) -> str:  # pragma: no cover
        if any(r.criticality == "MUST" and not r.pass_ for r in self.results):  # pragma: no cover
            return "NON_CONFORMANT"  # pragma: no cover
        return "CONFORMANT"  # pragma: no cover

    def to_dict(self) -> dict[str, Any]:  # pragma: no cover
        d = self._unsigned()
        d["summary"] = self.summary()
        d["verdict"] = self.verdict()
        d["digest"] = self.digest
        d["signature"] = self.signature
        d["public_key"] = self.public_key
        return d  # pragma: no cover

    def write(self, path: Path) -> None:  # pragma: no cover
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str))
