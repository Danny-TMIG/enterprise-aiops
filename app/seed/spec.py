from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.seed.intent import Intent


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Invariant:
    name: str
    statement: str
    kind: str = "property"    # property | safety | liveness | type

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "statement": self.statement, "kind": self.kind}


@dataclass
class Spec:
    intent_id: str
    what: str
    where: str
    invariants: list[Invariant] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    frozen: bool = False
    frozen_at: str = ""
    id: str = ""

    def freeze(self) -> Spec:
        self.frozen = True
        self.frozen_at = _now()
        self.id = self._hash()
        return self

    def _hash(self) -> str:
        blob = json.dumps({
            "intent_id": self.intent_id,
            "what": self.what, "where": self.where,
            "invariants": [i.to_dict() for i in self.invariants],
            "acceptance": self.acceptance,
            "out_of_scope": self.out_of_scope,
        }, sort_keys=True)
        return "spec-" + hashlib.sha256(blob.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "intent_id": self.intent_id,
            "what": self.what, "where": self.where,
            "invariants": [i.to_dict() for i in self.invariants],
            "acceptance": self.acceptance,
            "out_of_scope": self.out_of_scope,
            "frozen": self.frozen, "frozen_at": self.frozen_at,
        }


def draft(intent: Intent) -> Spec:
    """Deterministic spec draft from intent. Not an LLM — a contract
    skeleton the human will edit. This is the 'spec' the mesh shows
    at gate 1."""
    what = intent.raw.strip().rstrip(".")
    where = intent.target or _infer_target(intent)
    return Spec(
        intent_id=intent.id,
        what=what,
        where=where,
        invariants=[
            Invariant(name="no_regression",
                      statement="existing behaviour for the touched surface is preserved",
                      kind="safety"),
            Invariant(name="bounded_resource",
                      statement="resource use stays within declared limits",
                      kind="property"),
        ],
        acceptance=[
            "unit tests for the new behaviour pass",
            "existing tests for the touched surface still pass",
            "scan reports no new high-severity findings",
            "kernel-checked proof object emitted",
        ],
        out_of_scope=[
            "changes outside the declared 'where' path",
        ],
    )


def _infer_target(intent: Intent) -> str:
    for kw in intent.keywords:
        if "/" in kw:
            return kw
    for kw in intent.keywords:
        if kw.endswith(".py"):
            return kw
    return "app/"
