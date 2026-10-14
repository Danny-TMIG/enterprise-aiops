"""Every predicate in contracts/predicates must be true on a valid object.

This test suite is the executable form of the FAS contract invariants.
Implementation code will be written against these predicates; any
implementation whose behavior fails a predicate is not conformant.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from contracts.predicates import envelope, fail_closed, idempotency, authority, evidence, information_flow


# ---------------------------------------------------------------- envelope
VALID_ENVELOPE = {
    "schema_version": "1.0",
    "object_id": "obj-001",
    "correlation_id": "corr-001",
    "causation_id": "caus-001",
    "sovereign_domain": "domain-a",
    "purpose": "test",
    "classification": "internal",
    "issued_at": "2026-10-13T00:00:00Z",
    "valid_until": "2026-10-14T00:00:00Z",
    "integrity": "abcdef0123456789",
    "evidence_refs": ["ev-001"],
}


def test_is_envelope_accepts_valid():
    assert envelope.is_envelope(VALID_ENVELOPE)


def test_is_envelope_rejects_missing_field():
    bad = dict(VALID_ENVELOPE)
    del bad["correlation_id"]
    assert not envelope.is_envelope(bad)


def test_is_envelope_rejects_non_dict():
    assert not envelope.is_envelope("not a dict")


def test_has_correlation():
    assert envelope.has_correlation(VALID_ENVELOPE)


def test_has_validity_window():
    assert envelope.has_validity_window(VALID_ENVELOPE)


def test_is_expired_now_false():
    assert not envelope.is_expired(VALID_ENVELOPE, "2026-10-13T12:00:00Z")


def test_is_expired_now_true():
    assert envelope.is_expired(VALID_ENVELOPE, "2026-10-15T00:00:00Z")


def test_has_integrity():
    assert envelope.has_integrity(VALID_ENVELOPE)


# ---------------------------------------------------------------- fail-closed
def _echo_deny(obj):
    if not isinstance(obj, dict) or "bad" in obj:
        return {"status": "deny"}
    return {"status": "allow"}


def test_rejects_invalid():
    assert fail_closed.rejects_invalid(_echo_deny, {"bad": True})


def test_is_rejected():
    assert fail_closed.is_rejected({"status": "deny"})
    assert fail_closed.is_rejected({"status": "error"})


def test_is_accepted():
    assert fail_closed.is_accepted({"status": "allow"})


def test_rejects_expired():
    assert fail_closed.rejects_expired(_echo_deny, {"bad": True})


def test_rejects_unsigned():
    assert fail_closed.rejects_unsigned(_echo_deny, {"bad": True})


# ---------------------------------------------------------------- idempotency
def test_has_idempotency_key():
    assert idempotency.has_idempotency_key({"idempotency_key": "key-abcdef"})


def test_has_idempotency_key_too_short():
    assert not idempotency.has_idempotency_key({"idempotency_key": "abc"})


def test_retry_is_stable():
    assert idempotency.retry_is_stable("k1", ["k1", "k2"])


class _Counter:
    value = 0


def test_retry_does_not_duplicate_effect():
    counter = _Counter()
    seen = set()

    def send(obj):
        key = obj["idempotency_key"]
        if key not in seen:
            seen.add(key)
            counter.value += 1
        return {"status": "ok"}

    assert idempotency.retry_does_not_duplicate_effect(counter, send, {"idempotency_key": "k-abcdef"})


def test_duplicate_delivery_is_inert():
    def send(obj):
        return {"status": "ok"}
    assert idempotency.duplicate_delivery_is_inert(send, {"idempotency_key": "k-abcdef"})


# ---------------------------------------------------------------- authority
def test_cognition_cannot_authorize():
    assert not authority.cognition_cannot_authorize("cognition", "authorize")
    assert authority.cognition_cannot_authorize("cognition", "propose")


def test_govern_cannot_execute():
    assert not authority.govern_cannot_execute("govern", "execute")
    assert authority.govern_cannot_execute("govern", "authorize")


def test_compute_cannot_broaden_ok():
    o = {"capability_id": "cap-1", "max_quantity": 5}
    e = {"capability_id": "cap-1", "max_quantity": 5}
    assert authority.compute_cannot_broaden(o, e)


def test_compute_cannot_broaden_quantity():
    o = {"capability_id": "cap-1", "max_quantity": 5}
    e = {"capability_id": "cap-1", "max_quantity": 10}
    assert not authority.compute_cannot_broaden(o, e)


def test_compute_cannot_broaden_capability():
    o = {"capability_id": "cap-1"}
    e = {"capability_id": "cap-2"}
    assert not authority.compute_cannot_broaden(o, e)


def test_delegation_does_not_amplify_ok():
    p = {"subject": "alice", "action": "read", "valid_until": "2026-11-01T00:00:00Z"}
    c = {"subject": "alice", "action": "read", "valid_until": "2026-10-20T00:00:00Z"}
    assert authority.delegation_does_not_amplify(p, c)


def test_delegation_amplifies_scope():
    p = {"subject": "alice", "action": "read"}
    c = {"subject": "alice", "action": "write"}
    assert not authority.delegation_does_not_amplify(p, c)


def test_delegation_amplifies_time():
    p = {"subject": "alice", "action": "read", "valid_until": "2026-10-20T00:00:00Z"}
    c = {"subject": "alice", "action": "read", "valid_until": "2026-12-31T00:00:00Z"}
    assert not authority.delegation_does_not_amplify(p, c)


def test_revocation_blocks_new_orders():
    assert not authority.revocation_blocks_new_orders({"alice"}, "alice")
    assert authority.revocation_blocks_new_orders({"bob"}, "alice")


# ---------------------------------------------------------------- evidence
def test_has_evidence_ref():
    assert evidence.has_evidence_ref({"evidence_refs": ["ev-1"]})
    assert not evidence.has_evidence_ref({"evidence_refs": []})


def test_evidence_is_reconstructible():
    run = {
        "intent_ref": "i-1", "identity_ref": "id-1", "authority_ref": "a-1",
        "execution_ref": "x-1", "outcome_ref": "o-1", "evidence_refs": ["ev-1"],
    }
    assert evidence.evidence_is_reconstructible(run)


def test_evidence_is_not_inferred_complete():
    assert not evidence.evidence_is_not_inferred_complete({"status": "success"})
    assert evidence.evidence_is_not_inferred_complete(
        {"status": "success", "evidence_refs": ["ev-1"]}
    )


def test_cancellation_is_observable():
    assert evidence.cancellation_is_observable(
        {"status": "cancelled", "transition_ref": "t-1", "failure_reason": None}
    )
    assert not evidence.cancellation_is_observable(
        {"status": "cancelled", "failure_reason": "timeout"}
    )


# ---------------------------------------------------------------- information flow
def test_no_downgrade():
    assert information_flow.no_downgrade("internal", "internal")
    assert information_flow.no_downgrade("internal", "confidential")
    assert not information_flow.no_downgrade("confidential", "internal")


def test_representation_is_least_disclosing():
    r = {"representation_class": "redacted"}
    assert information_flow.representation_is_least_disclosing(r, "full")
    assert information_flow.representation_is_least_disclosing(r, "redacted")
    assert not information_flow.representation_is_least_disclosing(
        {"representation_class": "full"}, "redacted"
    )
