"""Smoke tests for the Governance Kernel group."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(rel: str, name: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ENV = {
    "schema_version": "1.0",
    "object_id": "obj-1",
    "correlation_id": "corr-1",
    "sovereign_domain": "tmig.local",
    "issuer": "test",
    "purpose": "smoke",
    "classification": "internal",
    "event_time": "2026-10-14T00:00:00Z",
    "integrity": {"algorithm": "sha256", "digest": "0" * 64},
}


def test_krn002_transition_and_rejection():
    mod = load(
        "components/ag/GOV-KRN-002-governed-state-and-transition-engine/src/public/engine.py",
        "krn002",
    )
    with mod.TransitionEngine() as eng:
        t1 = eng.record("s-1", "NEW", "APPROVED", "alice", "review", ENV)
        assert t1.seq == 1
        t2 = eng.record("s-1", "APPROVED", "EXECUTED", "bob", "run", ENV)
        assert t2.seq == 2
        assert t2.prev_hash == t1.chain_hash
        assert eng.current_state("s-1") == "EXECUTED"
        assert eng.verify_chain("s-1") is True

        bad = dict(ENV)
        bad.pop("schema_version")
        try:
            eng.record("s-2", "NEW", "APPROVED", "x", "y", bad)
        except mod.EnvelopeError:
            pass
        else:
            raise AssertionError("expected EnvelopeError for missing schema_version")

        try:
            eng.record("s-1", "EXECUTED", "CLOSED", "x", "y", ENV, expected_seq=1)
        except mod.ConcurrencyError:
            pass
        else:
            raise AssertionError("expected ConcurrencyError on stale expected_seq")


def test_krn003_correlation():
    mod = load(
        "components/ag/GOV-KRN-003-decision-and-outcome-correlation/src/public/correlation.py",
        "krn003",
    )
    with mod.CorrelationRegistry() as reg:
        c = reg.open("corr-1", ["decision-1", "decision-2"])
        assert c.status == "OPEN"
        assert reg.verify("corr-1") is True

        closed = reg.close_with_outcome("corr-1", "outcome-1")
        assert closed.status == "CLOSED"
        assert closed.outcome_ref == "outcome-1"
        assert reg.verify("corr-1") is True

        try:
            reg.close_with_outcome("corr-1", "outcome-2")
        except mod.AlreadyClosedError:
            pass
        else:
            raise AssertionError("expected AlreadyClosedError on second close")
