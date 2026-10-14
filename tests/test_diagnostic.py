"""Run the full-stack cross-layer diagnostic and check its output."""
from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def diag(run):
    return run(["python3", "integration/e2e/test_full_stack_diagnostic.py"], timeout=600)


def test_diagnostic_exits_zero(diag):
    assert diag.returncode == 0, (
        f"exit {diag.returncode}\n--- stdout ---\n{diag.stdout}\n"
        f"--- stderr ---\n{diag.stderr}"
    )


def test_diagnostic_reports_success(diag):
    combined = diag.stdout + diag.stderr
    assert "[SUCCESS] Full-stack cross-layer diagnostic test passed" in combined


def test_diagnostic_checks_each_layer(diag):
    combined = diag.stdout + diag.stderr
    for tag in ("[AC]", "[AG]", "[AX]"):
        assert tag in combined, f"layer check {tag} missing from diagnostic output"
