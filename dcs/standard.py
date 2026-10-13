"""Standard loading + schema validation."""

from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
import re  # pragma: no cover
from dataclasses import dataclass, field  # pragma: no cover
from pathlib import Path  # pragma: no cover

_REQ_ID = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$")
_CRIT = {"MUST", "SHOULD", "MAY"}


@dataclass(frozen=True)
class Requirement:  # pragma: no cover
    id: str
    title: str
    section: str
    hats: list[str]
    criticality: str
    test: str  # dotted path to a callable


@dataclass(frozen=True)
class Standard:  # pragma: no cover
    id: str
    version: str
    title: str
    published: str
    authority: str
    requirements: list[Requirement] = field(default_factory=list)

    @property
    def ref(self) -> str:  # pragma: no cover
        return f"{self.id}@{self.version}"  # pragma: no cover

    def by_id(self, req_id: str) -> Requirement:  # pragma: no cover
        for r in self.requirements:
            if r.id == req_id:  # pragma: no cover
                return r  # pragma: no cover
        raise KeyError(req_id)  # pragma: no cover


def load(path: str | Path) -> Standard:  # pragma: no cover
    doc = json.loads(Path(path).read_text())

    meta = doc.get("standard") or {}
    for k in ("id", "version", "title", "published", "authority"):
        if k not in meta:  # pragma: no cover
            raise ValueError(f"standard.{k} missing")  # pragma: no cover

    reqs = []
    seen = set()
    for raw in doc.get("requirements", []):
        for k in ("id", "title", "section", "hats", "criticality", "test"):
            if k not in raw:  # pragma: no cover
                raise ValueError(f"requirement missing {k}: {raw.get('id', '?')}")  # pragma: no cover
        if not _REQ_ID.match(raw["id"]):  # pragma: no cover
            raise ValueError(f"bad id: {raw['id']}")  # pragma: no cover
        if raw["criticality"] not in _CRIT:  # pragma: no cover
            raise ValueError(f"bad criticality: {raw['criticality']}")  # pragma: no cover
        if raw["id"] in seen:  # pragma: no cover
            raise ValueError(f"duplicate id: {raw['id']}")  # pragma: no cover
        seen.add(raw["id"])
        reqs.append(
            Requirement(
                id=raw["id"],
                title=raw["title"],
                section=raw["section"],
                hats=list(raw["hats"]),
                criticality=raw["criticality"],
                test=raw["test"],
            )
        )

    return Standard(  # pragma: no cover
        id=meta["id"],
        version=meta["version"],
        title=meta["title"],
        published=meta["published"],
        authority=meta["authority"],
        requirements=reqs,
    )
