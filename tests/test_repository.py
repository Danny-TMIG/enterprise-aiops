"""Structural invariants of the ASF repository."""
from __future__ import annotations

from pathlib import Path

import pytest


LAYERS = ("ax", "ag", "ac")
EXPECTED_LAYER_COUNTS = {"ax": 42, "ag": 48, "ac": 60}
EXPECTED_TOTAL = 150


def _component_dirs(root: Path, layer: str) -> list[Path]:
    """Directories only. Excludes __init__.py, __pycache__, hidden dirs."""
    d = root / "components" / layer
    if not d.is_dir():
        return []
    return sorted(
        p for p in d.iterdir()
        if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
    )


def test_repo_root_exists(repo_root):
    assert repo_root.is_dir()
    assert (repo_root / "pyproject.toml").is_file()


def test_required_top_level_dirs(repo_root):
    required = ["catalog", "components", "contracts", "deploy",
                "docs", "integration", "libraries", "tooling", "tests"]
    missing = [d for d in required if not (repo_root / d).is_dir()]
    assert not missing, f"missing top-level dirs: {missing}"


def test_layer_directory_counts(repo_root):
    actual = {layer: len(_component_dirs(repo_root, layer)) for layer in LAYERS}
    assert actual == EXPECTED_LAYER_COUNTS, (
        f"layer directory counts mismatch: {actual} != {EXPECTED_LAYER_COUNTS}"
    )


def test_components_total_is_150(repo_root):
    total = sum(len(_component_dirs(repo_root, l)) for l in LAYERS)
    assert total == EXPECTED_TOTAL, (
        f"expected {EXPECTED_TOTAL} component dirs, found {total}"
    )


def test_canonical_schemas_present(repo_root):
    d = repo_root / "contracts" / "canonical"
    assert d.is_dir(), "contracts/canonical missing"
    schemas = list(d.glob("*.json"))
    assert len(schemas) >= 20, f"expected >=20 canonical schemas, found {len(schemas)}"


def test_catalog_inventories_present(repo_root):
    d = repo_root / "catalog" / "inventories"
    assert d.is_dir(), "catalog/inventories missing"
