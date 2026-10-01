"""Standard loading + schema validation."""
from __future__ import annotations
import json, re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

_REQ_ID = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$")
_CRIT = {"MUST", "SHOULD", "MAY"}


@dataclass(frozen=True)
class Requirement:
    id: str
    title: str
    section: str
    hats: List[str]
    criticality: str
    test: str           # dotted path to a callable


@dataclass(frozen=True)
class Standard:
    id: str
    version: str
    title: str
    published: str
    authority: str
    requirements: List[Requirement] = field(default_factory=list)

    @property
    def ref(self) -> str:
        return f"{self.id}@{self.version}"

    def by_id(self, req_id: str) -> Requirement:
        for r in self.requirements:
            if r.id == req_id:
                return r
        raise KeyError(req_id)


def load(path: str | Path) -> Standard:
    doc = json.loads(Path(path).read_text())

    meta = doc.get("standard") or {}
    for k in ("id", "version", "title", "published", "authority"):
        if k not in meta:
            raise ValueError(f"standard.{k} missing")

    reqs = []
    seen = set()
    for raw in doc.get("requirements", []):
        for k in ("id", "title", "section", "hats", "criticality", "test"):
            if k not in raw:
                raise ValueError(f"requirement missing {k}: {raw.get('id','?')}")
        if not _REQ_ID.match(raw["id"]):
            raise ValueError(f"bad id: {raw['id']}")
        if raw["criticality"] not in _CRIT:
            raise ValueError(f"bad criticality: {raw['criticality']}")
        if raw["id"] in seen:
            raise ValueError(f"duplicate id: {raw['id']}")
        seen.add(raw["id"])
        reqs.append(Requirement(
            id=raw["id"], title=raw["title"], section=raw["section"],
            hats=list(raw["hats"]), criticality=raw["criticality"],
            test=raw["test"],
        ))

    return Standard(
        id=meta["id"], version=meta["version"], title=meta["title"],
        published=meta["published"], authority=meta["authority"],
        requirements=reqs,
    )
