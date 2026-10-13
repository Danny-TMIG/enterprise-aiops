from __future__ import annotations

import re

from app.reconfig.intent_ir import IntentIR

_VERBS = {
    "count": "COUNT", "sum": "SUM", "reverse": "REVERSE",
    "train": "TRAIN", "classify": "CLASSIFY", "evaluate": "EVALUATE",
    "store": "STORE", "save": "STORE", "persist": "STORE",
    "read": "READ", "load": "LOAD", "fetch": "FETCH",
    "route": "ROUTE", "send": "ROUTE", "emit": "EMIT",
    "filter": "FILTER", "join": "JOIN", "aggregate": "AGGREGATE",
    "retrain": "RETRAIN", "schedule": "SCHEDULE", "record": "RECORD",
    "verify": "VERIFY", "validate": "VALIDATE",
}

_TARGETS = {
    "postgres": "pg", "postgresql": "pg", "pg": "pg", "sql": "pg",
    "mongo": "mongo", "mongodb": "mongo", "mql": "mongo",
    "redis": "redis", "kafka": "kafka", "slack": "slack",
    "s3": "s3", "python": "python", "js": "js", "typescript": "ts",
    "rust": "rust",
}

_OBJECT_ROLES = {
    r"\bstrings?\b": "input",
    r"\bwords?\b": "input",
    r"\blists?\b": "input",
    r"\bevents?\b": "input",
    r"\bresults?\b": "output",
    r"\bcounts?\b": "output",
    r"\blabels?\b": "output",
}

_CONSTRAINT_PATTERNS = [
    (r"must (?:be|run) (\w[\w\s]*)", "must:{}"),
    (r"within (\d+)\s*(seconds?|minutes?|hours?)", "within:{}"),
    (r"without (\w[\w\s]*)", "without:{}"),
    (r"no (\w[\w\s]*)", "no:{}"),
]

_EVIDENCE_PATTERNS = [
    (r"\b(test|tests|tested)\b", "tests"),
    (r"\b(benchmark|bench)\b", "benchmark"),
    (r"\b(proof|prove)\b", "proof"),
    (r"\b(evidence|attest)\b", "attestation"),
    (r"\b(verify|validation)\b", "validation"),
]


def interpret(raw: str, source: str = "user") -> IntentIR:
    text = raw.strip()
    low = text.lower()

    verbs = []
    for w, v in _VERBS.items():
        if re.search(rf"\b{re.escape(w)}\b", low) and v not in verbs:
            verbs.append(v)

    targets = []
    for w, t in _TARGETS.items():
        if re.search(rf"\b{re.escape(w)}\b", low) and t not in targets:
            targets.append(t)

    objects: dict[str, str] = {}
    for pat, role in _OBJECT_ROLES.items():
        m = re.search(pat, low)
        if m and role not in objects:
            objects[role] = m.group(0).strip()

    constraints = []
    for pat, fmt in _CONSTRAINT_PATTERNS:
        for m in re.finditer(pat, low):
            constraints.append(fmt.format(m.group(1).strip()))

    evidence = []
    for pat, ev in _EVIDENCE_PATTERNS:
        if re.search(pat, low) and ev not in evidence:
            evidence.append(ev)

    # residue: anything with an adjectival quality that has no projection
    residue = []
    for w in ("beautiful", "tasteful", "elegant", "funny", "inspiring"):
        if w in low:
            residue.append(w)

    return IntentIR(
        goal=text,
        verbs=verbs,
        objects=objects,
        targets=targets,
        constraints=constraints,
        evidence_required=evidence,
        residue=residue,
        raw=raw,
        source=source,
    )
