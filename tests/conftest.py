"""Root fixtures for the ASF test suite."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return p.parent.parent


ROOT = _repo_root()


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def components_dir(repo_root: Path) -> Path:
    return repo_root / "components"


@pytest.fixture(scope="session")
def run():
    """Return a function that runs a command from the repo root."""
    def _run(cmd, cwd=None, timeout=600):
        return subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    return _run
