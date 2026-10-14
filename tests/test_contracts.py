"""Validate every canonical schema is parseable and non-empty."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def _schemas(repo_root: Path) -> list[Path]:
    d = repo_root / "contracts" / "canonical"
    if not d.is_dir():
        return []
    return sorted(d.glob("*.json"))


def test_schemas_exist(repo_root):
    assert _schemas(repo_root), "no canonical schemas found"


def test_every_schema_is_valid_json(repo_root):
    bad = []
    for s in _schemas(repo_root):
        try:
            json.loads(s.read_text())
        except json.JSONDecodeError as e:
            bad.append(f"{s.name}: {e}")
    assert not bad, f"{len(bad)} invalid schemas:\n" + "\n".join(bad)


def test_every_schema_is_nonempty_object(repo_root):
    """Every schema must be a JSON object with at least one key.

    We do NOT require $schema / $id / title — some schemas in this repo
    are deliberately minimal and rely on the Common Envelope for identity.
    """
    bad = []
    for s in _schemas(repo_root):
        d = json.loads(s.read_text())
        if not isinstance(d, dict):
            bad.append(f"{s.name}: not an object")
        elif not d:
            bad.append(f"{s.name}: empty object")
    assert not bad, f"bad schemas: {bad}"
