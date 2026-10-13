"""Deterministic artifact generation.

We do not call an LLM here. We emit a *shape* — file + tests + proof
target — derived from the frozen spec. This is what the mesh ships
to scan/prove. The shape is a real diff the human reviews at gate 2.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.seed.spec import Spec


@dataclass
class Artifact:
    spec_id: str
    files: dict[str, str] = field(default_factory=dict)
    tests: dict[str, str] = field(default_factory=dict)
    proof_target: str = ""
    summary: str = ""
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            blob = json.dumps({
                "spec_id": self.spec_id,
                "files": sorted(self.files),
                "tests": sorted(self.tests),
                "proof_target": self.proof_target,
            }, sort_keys=True)
            self.id = "art-" + hashlib.sha256(blob.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "spec_id": self.spec_id,
            "files": list(self.files.keys()),
            "tests": list(self.tests.keys()),
            "proof_target": self.proof_target,
            "summary": self.summary,
        }


def generate(spec: Spec) -> Artifact:
    if not spec.frozen:
        raise ValueError("spec must be frozen before artifact generation")

    slug = _slug(spec.what)
    target_path = _target_path(spec.where, slug)

    module_src = (
        f'"""Generated for spec {spec.id}.\n\n'
        f'What: {spec.what}\n'
        f'Where: {spec.where}\n"""\n'
        f"from __future__ import annotations\n\n\n"
        f"def {slug}(value: int) -> int:\n"
        f'    """{spec.what}."""\n'
        f"    if not isinstance(value, int):\n"
        f"        raise TypeError('value must be int')\n"
        f"    return value + 1\n"
    )

    test_src = (
        f'"""Generated tests for spec {spec.id}."""\n'
        f"import pytest\n\n"
        f"from {_module_import(target_path)} import {slug}\n\n\n"
        f"def test_{slug}_basic():\n"
        f"    assert {slug}(0) == 1\n"
        f"    assert {slug}(-1) == 0\n\n\n"
        f"def test_{slug}_type_error():\n"
        f"    with pytest.raises(TypeError):\n"
        f"        {slug}('x')\n"
    )

    proof_target = f"theorem spec_{spec.id.replace('-', '_')} : True := by trivial"

    return Artifact(
        spec_id=spec.id,
        files={target_path: module_src},
        tests={f"tests/test_{slug}.py": test_src},
        proof_target=proof_target,
        summary=f"add {slug} at {target_path}",
    )


def _slug(text: str) -> str:
    toks = re.findall(r"[A-Za-z0-9]+", text.lower())
    toks = [t for t in toks if t not in ("a", "an", "the", "to", "for",
                                         "of", "in", "on", "and", "or",
                                         "add", "implement", "create")]
    return "_".join(toks[:4]) or "mesh_task"


def _target_path(where: str, slug: str) -> str:
    w = (where or "app").rstrip("/")
    if w.endswith(".py"):
        return w
    return f"{w}/{slug}.py"


def _module_import(path: str) -> str:
    return path[:-3].replace("/", ".")
