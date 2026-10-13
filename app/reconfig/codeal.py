"""Code-AL — the code assembly language.

A graph-shaped IR. Every target language (Python, SQL, MQL, RL,
ML) compiles to the same Code-AL graph. The graph hashes.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

OPS = {
    "LOAD", "FETCH", "STORE", "COUNT", "SUM", "FILTER", "JOIN",
    "AGGREGATE", "TRAIN", "EVALUATE", "RETRAIN", "SCHEDULE",
    "ROUTE", "RECORD", "EMIT", "VERIFY", "VALIDATE", "REVERSE",
    "CLASSIFY", "READ",
}


def _h(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()[:24]


@dataclass
class CAInstruction:
    id: str
    op: str
    slots: dict[str, str] = field(default_factory=dict)     # name → ref | literal
    residue: list[str] = field(default_factory=list)

    def to_canonical(self) -> str:
        return json.dumps(
            {"id": self.id, "op": self.op,
             "slots": {k: self.slots[k] for k in sorted(self.slots)},
             "residue": sorted(self.residue)},
            sort_keys=True, separators=(",", ":"),
        )


@dataclass
class CAProgram:
    name: str
    instructions: list[CAInstruction] = field(default_factory=list)
    residue: list[str] = field(default_factory=list)

    def hash(self) -> str:
        body = "\n".join(i.to_canonical() for i in self.instructions)
        return _h(f"ca/{self.name}/{body}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "hash": self.hash(),
            "instructions": [asdict(i) for i in self.instructions],
            "residue": self.residue,
        }


def from_tasks(name: str, tasks: list[Any]) -> CAProgram:
    prog = CAProgram(name=name)
    for t in tasks:
        op = t.op if t.op in OPS else "EMIT"
        slots: dict[str, str] = {}
        for i, inp in enumerate(t.inputs):
            slots[f"in{i}"] = inp
        for i, out in enumerate(t.outputs):
            slots[f"out{i}"] = out
        for k, v in (t.params or {}).items():
            slots[k] = str(v)
        prog.instructions.append(CAInstruction(
            id=t.id, op=op, slots=slots, residue=list(getattr(t, "residue", []))
        ))
        for r in getattr(t, "residue", []) or []:
            if r not in prog.residue:
                prog.residue.append(r)
    return prog
