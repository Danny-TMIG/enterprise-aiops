"""Unit tests for the Governance Kernel group."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def krn001():
    return _load(
        "components/ag/GOV-KRN-001-governance-object-model-and-registry/src/public/registry.py",
        "krn001",
    )


@pytest.fixture(scope="module")
def krn002():
    return _load(
        "components/ag/GOV-KRN-002-governed-state-and-transition-engine/src/public/engine.py",
        "krn002",
    )


@pytest.fixture(scope="module")
def krn003():
    return _load(
        "components/ag/GOV-KRN-003-decision-and-outcome-correlation/src/public/correlation.py",
        "krn003",
    )


ENVELOPE = {
    "schema_version": "1.0",
    "object_id": "obj-1",
    "correlation_id": "corr-1",
    "sovereign_domain": "tmig.local",
    "issuer": "test",
    "purpose": "unit",
    "classification": "internal",
    "event_time": "2026-10-14T00:00:00Z",
    "integrity": {"algorithm": "sha256", "digest": "0" * 64},
}


# ---------------- GOV-KRN-001 ----------------

def test_krn001_put_first_version(krn001):
    with krn001.GovernanceRegistry() as reg:
        obj = reg.put("o1", "policy", {"rule": "deny"})
        assert obj.version == 1
        assert obj.prev_hash is None
        assert obj.chain_hash


def test_krn001_second_version_links_hash(krn001):
    with krn001.GovernanceRegistry() as reg:
        a = reg.put("o1", "policy", {"rule": "deny"})
        b = reg.put("o1", "policy", {"rule": "allow"})
        assert b.version == 2
        assert b.prev_hash == a.chain_hash


def test_krn001_stale_expected_version_raises(krn001):
    with krn001.GovernanceRegistry() as reg:
        reg.put("o1", "policy", {"rule": "a"})
        with pytest.raises(krn001.ImmutableVersionError):
            reg.put("o1", "policy", {"rule": "b"}, expected_version=5)


def test_krn001_get_specific_version(krn001):
    with krn001.GovernanceRegistry() as reg:
        reg.put("o1", "policy", {"rule": "deny"})
        reg.put("o1", "policy", {"rule": "allow"})
        assert reg.get("o1", 1).payload == {"rule": "deny"}


def test_krn001_get_unknown_raises(krn001):
    with krn001.GovernanceRegistry() as reg:
        with pytest.raises(krn001.RegistryError):
            reg.get("nope")


def test_krn001_verify_chain_detects_tamper(krn001):
    with krn001.GovernanceRegistry() as reg:
        reg.put("o1", "policy", {"rule": "deny"})
        reg.put("o1", "policy", {"rule": "allow"})
        assert reg.verify_chain("o1") is True
        reg._conn.execute(
            "UPDATE governance_objects SET payload_json = ? WHERE object_id = ? AND version = ?",
            ('{"rule":"tampered"}', "o1", 1),
        )
        reg._conn.commit()
        assert reg.verify_chain("o1") is False


def test_krn001_list_ids_filters_by_kind(krn001):
    with krn001.GovernanceRegistry() as reg:
        reg.put("a", "policy", {})
        reg.put("b", "role", {})
        assert reg.list_ids("policy") == ["a"]
        assert reg.list_ids("role") == ["b"]


# ---------------- GOV-KRN-002 ----------------

def test_krn002_first_transition(krn002):
    with krn002.TransitionEngine() as eng:
        t = eng.record("s1", "NEW", "OPEN", "alice", "start", ENVELOPE)
        assert t.seq == 1
        assert t.prev_hash is None
        assert eng.current_state("s1") == "OPEN"


def test_krn002_second_transition_links_hash(krn002):
    with krn002.TransitionEngine() as eng:
        a = eng.record("s1", "NEW", "OPEN", "alice", "start", ENVELOPE)
        b = eng.record("s1", "OPEN", "CLOSED", "bob", "done", ENVELOPE)
        assert b.seq == 2
        assert b.prev_hash == a.chain_hash


@pytest.mark.parametrize("missing", [
    "schema_version", "object_id", "correlation_id", "sovereign_domain",
    "issuer", "purpose", "classification", "event_time", "integrity",
])
def test_krn002_rejects_incomplete_envelope(krn002, missing):
    with krn002.TransitionEngine() as eng:
        bad = {k: v for k, v in ENVELOPE.items() if k != missing}
        with pytest.raises(krn002.EnvelopeError):
            eng.record("s1", "NEW", "OPEN", "a", "r", bad)


def test_krn002_stale_expected_seq_raises(krn002):
    with krn002.TransitionEngine() as eng:
        eng.record("s1", "NEW", "OPEN", "a", "r", ENVELOPE)
        with pytest.raises(krn002.ConcurrencyError):
            eng.record("s1", "OPEN", "CLOSED", "a", "r", ENVELOPE, expected_seq=5)


def test_krn002_verify_chain_detects_tamper(krn002):
    with krn002.TransitionEngine() as eng:
        eng.record("s1", "NEW", "OPEN", "a", "r", ENVELOPE)
        eng.record("s1", "OPEN", "CLOSED", "a", "r", ENVELOPE)
        assert eng.verify_chain("s1") is True
        eng._conn.execute(
            "UPDATE transitions SET reason = ? WHERE subject_id = ? AND seq = ?",
            ("tampered", "s1", 1),
        )
        eng._conn.commit()
        assert eng.verify_chain("s1") is False


def test_krn002_empty_subject_raises(krn002):
    with krn002.TransitionEngine() as eng:
        with pytest.raises(krn002.TransitionError):
            eng.record("", "NEW", "OPEN", "a", "r", ENVELOPE)


# ---------------- GOV-KRN-003 ----------------

def test_krn003_open_creates_record(krn003):
    with krn003.CorrelationRegistry() as reg:
        c = reg.open("c1", ["d1"])
        assert c.status == "OPEN"
        assert c.outcome_ref is None


def test_krn003_open_rejects_duplicate(krn003):
    with krn003.CorrelationRegistry() as reg:
        reg.open("c1", ["d1"])
        with pytest.raises(krn003.CorrelationError):
            reg.open("c1", ["d2"])


def test_krn003_open_requires_decision(krn003):
    with krn003.CorrelationRegistry() as reg:
        with pytest.raises(krn003.CorrelationError):
            reg.open("c1", [])


def test_krn003_close_records_outcome(krn003):
    with krn003.CorrelationRegistry() as reg:
        reg.open("c1", ["d1"])
        closed = reg.close_with_outcome("c1", "outcome-1")
        assert closed.status == "CLOSED"
        assert closed.outcome_ref == "outcome-1"


def test_krn003_double_close_raises(krn003):
    with krn003.CorrelationRegistry() as reg:
        reg.open("c1", ["d1"])
        reg.close_with_outcome("c1", "o1")
        with pytest.raises(krn003.AlreadyClosedError):
            reg.close_with_outcome("c1", "o2")


def test_krn003_close_unknown_raises(krn003):
    with krn003.CorrelationRegistry() as reg:
        with pytest.raises(krn003.CorrelationError):
            reg.close_with_outcome("nope", "o1")


def test_krn003_open_correlations_lists_open_only(krn003):
    with krn003.CorrelationRegistry() as reg:
        reg.open("c1", ["d1"])
        reg.open("c2", ["d2"])
        reg.close_with_outcome("c1", "o1")
        assert reg.open_correlations() == ["c2"]
