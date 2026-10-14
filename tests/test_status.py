"""Run tooling/validation/status.py and check its contract."""
from __future__ import annotations

import json

import pytest


def test_status_human_run(run):
    r = run(["python3", "tooling/validation/status.py"])
    assert r.returncode in (0, 1), f"unexpected exit {r.returncode}\n{r.stderr}"
    assert "AETHER STATUS" in r.stdout
    assert "VERDICT:" in r.stdout
    for section in ("GIT", "TREE", "SIZE"):
        assert section in r.stdout, f"section {section} missing"


def test_status_json_run(run):
    r = run(["python3", "tooling/validation/status.py", "--json"])
    assert r.returncode in (0, 1), f"unexpected exit {r.returncode}\n{r.stderr}"
    d = json.loads(r.stdout)
    for key in ("git", "tree", "tracked", "verdict"):
        assert key in d, f"missing key {key}"
    assert d["verdict"]["status"] in ("OK", "ATTENTION")


def test_status_tree_counts(run):
    r = run(["python3", "tooling/validation/status.py", "--json"])
    d = json.loads(r.stdout)
    pl = d["tree"]["components_per_layer"]
    assert pl == {"ax": 42, "ag": 48, "ac": 60}, f"unexpected layer counts: {pl}"
    assert d["tree"]["components_total"] == 150
