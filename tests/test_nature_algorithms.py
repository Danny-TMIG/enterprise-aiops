"""Derived algorithms from the nature catalog."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CATALOG = ROOT / "data" / "nature.txt"
DERIVED = ROOT / "data" / "algorithms.json"


def test_source_catalog_exists():
    assert CATALOG.is_file()


def test_derived_catalog_exists():
    assert DERIVED.is_file()


def test_every_source_phenomenon_has_derived_algorithm():
    sources = set()
    for line in CATALOG.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        code = line.split("|")[0].strip()
        if code:
            sources.add(code)
    derived = json.loads(DERIVED.read_text())
    mapped = {a["phenomenon"] for a in derived["algorithms"]}
    missing = sources - mapped
    assert not missing, f"phenomena without derived algorithm: {missing}"


def test_every_derived_has_reference():
    derived = json.loads(DERIVED.read_text())
    for a in derived["algorithms"]:
        assert a["reference"], f"no reference for {a['algorithm']}"


def test_every_declared_algorithm_is_implemented_or_pending():
    from nature.algorithms import ALGORITHMS, PENDING
    derived = json.loads(DERIVED.read_text())
    known = set(ALGORITHMS) | PENDING
    for a in derived["algorithms"]:
        assert a["algorithm"] in known, f"unaccounted: {a['algorithm']}"


@pytest.mark.parametrize("algo", list(__import__("nature.algorithms", fromlist=["ALGORITHMS"]).ALGORITHMS))
def test_algorithm_step_runs(algo):
    from nature.algorithms import step
    state_map = {
        "levy_flight_step": {"x": 0.0, "n": 0},
        "wiener_step": {"x": 0.0, "n": 0},
        "kuramoto_step": {"theta": [0.0, 0.1], "omega": [1.0, 1.1], "n": 0},
        "logistic_growth": {"x": 0.5, "n": 0},
        "sir_step": {"S": 100.0, "I": 1.0, "R": 0.0, "n": 0},
        "hebbian_update": {"w": [[0.0, 0.0], [0.0, 0.0]], "x": [1.0, -1.0], "n": 0},
        "gray_scott_step": {"u": [[1.0]*4 for _ in range(4)],
                            "v": [[0.0]*4 for _ in range(4)], "n": 0},
        "fick_flux": {"c": [1.0, 0.5, 0.0, 0.5, 1.0], "n": 0},
    }
    out = step(algo, state_map[algo], {}, seed=42)
    assert out["n"] == 1
