"""The Book of Genesis — the reconciliation sequence.

Seven stages. Each stage takes the previous stage's output and
returns a new record. The chain is content-addressed end to end.

    Confess    enumerate what state exists
    Separate   partition by residual class
    Witness    collect evidence for each partition
    Judge      decide with a deterministic predicate
    Reconcile  bring the failed part back into alignment
    Rest       record the state as content-addressed
    Recreate   generate the successor
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


def _h(*parts: str) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update(p.encode("utf-8")); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()[:16]


@dataclass
class Confession:
    run_digest: str
    sins: list[dict] = field(default_factory=list)

    @property
    def id(self) -> str:
        return _h("confession", self.run_digest,
                  *[s["sin"] + s["subject"] for s in self.sins])


@dataclass
class Separation:
    confession_id: str
    partitions: dict[str, list[dict]] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return _h("separation", self.confession_id,
                  *sorted(self.partitions.keys()))


@dataclass
class Witness:
    separation_id: str
    evidence: dict[str, str] = field(default_factory=dict)

    @property
    def id(self) -> str:
        flat: list[str] = []
        for k in sorted(self.evidence.keys()):
            flat.append(k)
            flat.append(self.evidence[k])
        return _h("witness", self.separation_id, *flat)


@dataclass
class Judgment:
    witness_id: str
    verdicts: dict[str, str] = field(default_factory=dict)

    @property
    def id(self) -> str:
        flat: list[str] = []
        for k in sorted(self.verdicts.keys()):
            flat.append(k)
            flat.append(self.verdicts[k])
        return _h("judgment", self.witness_id, *flat)


@dataclass
class Reconciliation:
    judgment_id: str
    actions: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return _h("recon", self.judgment_id, *self.actions)


@dataclass
class Rest:
    reconciliation_id: str
    state_hash: str
    ts: float = field(default_factory=time.time)

    @property
    def id(self) -> str:
        return _h("rest", self.reconciliation_id, self.state_hash)


@dataclass
class Recreate:
    rest_id: str
    successor_digest: str
    notes: str = ""

    @property
    def id(self) -> str:
        return _h("recreate", self.rest_id, self.successor_digest)


# ── seven stages ────────────────────────────────────────────────
def confess(run) -> Confession:
    from app.canon.sins import detect_all
    sins = [s.to_dict() for s in detect_all([run])]
    return Confession(run_digest=run.digest, sins=sins)


def separate(c: Confession) -> Separation:
    parts: dict[str, list[dict]] = {}
    for s in c.sins:
        for rid in s.get("residuals", []):
            key = rid.split("-")[0] if "-" in rid else rid
            parts.setdefault(key, []).append(s)
    return Separation(confession_id=c.id, partitions=parts)


def witness(sep: Separation) -> Witness:
    ev: dict[str, str] = {}
    for key, items in sep.partitions.items():
        names = sorted(set(i["sin"] for i in items))
        ev[key] = f"{len(items)} sin(s) in class {key}: " + ",".join(names)
    return Witness(separation_id=sep.id, evidence=ev)


def judge(w: Witness) -> Judgment:
    verdicts: dict[str, str] = {}
    for key, ev in w.evidence.items():
        verdicts[key] = "PASS" if ev else "UNKNOWN"
    return Judgment(witness_id=w.id, verdicts=verdicts)


def reconcile(j: Judgment) -> Reconciliation:
    actions: list[str] = []
    for key in sorted(j.verdicts.keys()):
        v = j.verdicts[key]
        if v == "PASS":
            actions.append(f"apply remedy in class {key}")
        else:
            actions.append(f"escalate class {key} to manual review")
    return Reconciliation(judgment_id=j.id, actions=actions)


def rest(r: Reconciliation, state: Any) -> Rest:
    return Rest(reconciliation_id=r.id,
                state_hash=_h("state", r.id, repr(state)[:128]))


def recreate(rs: Rest, successor_digest: str) -> Recreate:
    return Recreate(rest_id=rs.id, successor_digest=successor_digest)


def genesis(run) -> dict:
    c = confess(run)
    s = separate(c)
    w = witness(s)
    j = judge(w)
    r = reconcile(j)
    rs = rest(r, run.digest)
    rc = recreate(rs, successor_digest=_h("next", rs.id))
    return {
        "stages": ["confess", "separate", "witness", "judge",
                   "reconcile", "rest", "recreate"],
        "confession_id": c.id,
        "separation_id": s.id,
        "witness_id": w.id,
        "judgment_id": j.id,
        "reconciliation_id": r.id,
        "rest_id": rs.id,
        "recreate_id": rc.id,
        "n_sins": len(c.sins),
        "n_partitions": len(s.partitions),
        "verdicts": j.verdicts,
        "actions": r.actions,
        "successor_digest": rc.successor_digest,
    }
