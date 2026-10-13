from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.dominion.verdict import PASS, Verdict


def _h(*p: str) -> str:
    m = hashlib.sha256()
    for s in p:
        m.update(s.encode("utf-8")); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()[:24]


@dataclass
class Witness:
    role_id: str
    kind: str
    payload: Any
    verify_fn: Callable[[Any], Verdict] | None = None
    residue: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return _h("witness", self.role_id, self.kind,
                  repr(self.payload)[:128])

    def verify(self) -> Verdict:
        if self.verify_fn is None:
            return Verdict.make(PASS, f"{self.role_id}.trivial",
                                self.payload, repr(self.payload),
                                "no checker; witness accepted")
        return self.verify_fn(self.payload)

    def to_dict(self) -> dict[str, Any]:
        v = self.verify()
        return {
            "id": self.id,
            "role": self.role_id,
            "kind": self.kind,
            "verdict": v.state,
            "verifier": v.verifier_id,
            "evidence": v.evidence[:120],
            "residue": self.residue,
            "inputs": self.inputs,
        }
