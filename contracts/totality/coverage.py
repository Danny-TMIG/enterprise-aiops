"""Totality of the registry space — every declared component is classified.

The tree has two directories per logical component (bare-ID and slugged).
Every directory must be classified into exactly one of the following
totality classes:

  - logical   — represents a FAS logical component
  - alias     — a bare-ID directory that aliases a slugged sibling
  - scaffold  — a directory that exists only as structure, with no code
  - orphan    — a directory with no matching logical component
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DirClass(str, Enum):
    LOGICAL = "logical"
    ALIAS = "alias"
    SCAFFOLD = "scaffold"
    ORPHAN = "orphan"


LOGICAL_ID_RE = re.compile(r"^(COG|GOV|CMP)-[A-Z]+-\d+$")
SLUGGED_ID_RE = re.compile(r"^(COG|GOV|CMP)-[A-Z]+-\d+-[a-z0-9-]+$")


@dataclass(frozen=True)
class DirInfo:
    path: str
    name: str
    layer: str
    classification: DirClass
    has_code: bool
    has_init: bool


def classify_dirs(repo_root: Path) -> list[DirInfo]:
    out = []
    for layer in ("ax", "ag", "ac"):
        d = repo_root / "components" / layer
        if not d.is_dir():
            continue
        for child in sorted(d.iterdir()):
            if not child.is_dir() or child.name.startswith("_"):
                continue
            has_code = bool(list(child.rglob("*.py"))) if child.is_dir() else False
            has_init = (child / "src" / "public" / "__init__.py").is_file()
            if LOGICAL_ID_RE.match(child.name):
                cls = DirClass.ALIAS if has_code else DirClass.SCAFFOLD
            elif SLUGGED_ID_RE.match(child.name):
                cls = DirClass.LOGICAL
            else:
                cls = DirClass.ORPHAN
            out.append(DirInfo(
                path=str(child.relative_to(repo_root)),
                name=child.name,
                layer=layer,
                classification=cls,
                has_code=has_code,
                has_init=has_init,
            ))
    return out


def summary(dirs: list[DirInfo]) -> dict[DirClass, int]:
    counts: dict[DirClass, int] = {c: 0 for c in DirClass}
    for d in dirs:
        counts[d.classification] += 1
    return counts
