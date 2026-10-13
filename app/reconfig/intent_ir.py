from __future__ import annotations

import hashlib
import time
from dataclasses import asdict, dataclass, field
from typing import Any


def _h(*p: str) -> str:
    m = hashlib.sha256()
    for s in p:
        m.update(s.encode("utf-8")); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()[:24]


@dataclass
class IntentIR:
    goal: str
    verbs: list[str] = field(default_factory=list)
    objects: dict[str, str] = field(default_factory=dict)   # role → noun
    targets: list[str] = field(default_factory=list)        # pg, mongo, ...
    constraints: list[str] = field(default_factory=list)     # must/must-not
    evidence_required: list[str] = field(default_factory=list)
    residue: list[str] = field(default_factory=list)
    raw: str = ""
    source: str = "user"
    ts: str = field(default_factory=lambda: time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    @property
    def id(self) -> str:
        return _h("intent", self.goal, "|".join(sorted(self.verbs)),
                  "|".join(sorted(self.objects.items())),
                  "|".join(sorted(self.targets)))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self); d["id"] = self.id; return d
