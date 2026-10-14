"""Run tooling/master_orchestrator.py and check the completion contract."""
from __future__ import annotations

import re

import pytest

COMPLETION_RE = re.compile(
    r"\[COMPLETE\] Master orchestration pipeline finished successfully"
)
OMEGA_RE = re.compile(r"Omega Seal:\s*([0-9a-f]{16,})")


@pytest.fixture(scope="module")
def orch(run):
    r = run(["python3", "tooling/master_orchestrator.py"], timeout=900)
    return r


def test_orchestrator_exits_zero(orch):
    assert orch.returncode == 0, (
        f"exit {orch.returncode}\n--- stdout ---\n{orch.stdout}\n"
        f"--- stderr ---\n{orch.stderr}"
    )


def test_orchestrator_prints_completion(orch):
    combined = orch.stdout + orch.stderr
    assert COMPLETION_RE.search(combined), (
        f"completion line not found in output:\n{combined[-2000:]}"
    )


def test_orchestrator_prints_omega_seal(orch):
    combined = orch.stdout + orch.stderr
    m = OMEGA_RE.search(combined)
    assert m, f"Omega Seal not found in output:\n{combined[-2000:]}"
    seal = m.group(1)
    assert len(seal) >= 16
