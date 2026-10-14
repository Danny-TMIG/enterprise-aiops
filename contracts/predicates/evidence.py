"""Predicates for the evidence chain."""
from __future__ import annotations

from typing import Any


def has_evidence_ref(obj: Any) -> bool:
    return (isinstance(obj, dict)
            and isinstance(obj.get("evidence_refs"), list)
            and len(obj["evidence_refs"]) > 0)


def evidence_is_reconstructible(run: dict[str, Any]) -> bool:
    """Predicate: a terminal run has every link needed to reconstruct intent -> outcome."""
    if not isinstance(run, dict):
        return False
    required = ("intent_ref", "identity_ref", "authority_ref",
                "execution_ref", "outcome_ref", "evidence_refs")
    return all(k in run for k in required)


def evidence_is_not_inferred_complete(run: dict[str, Any]) -> bool:
    """Predicate: absence of evidence is not treated as success."""
    if not isinstance(run, dict):
        return False
    if run.get("status") == "success":
        return bool(run.get("evidence_refs"))
    return True


def cancellation_is_observable(run: dict[str, Any]) -> bool:
    """Predicate: a cancelled run records cancellation as a transition, not a failure."""
    if not isinstance(run, dict):
        return False
    if run.get("status") == "cancelled":
        return run.get("failure_reason") is None and bool(run.get("transition_ref"))
    return True


def revocation_is_observable(run: dict[str, Any]) -> bool:
    if not isinstance(run, dict):
        return False
    if run.get("status") == "revoked":
        return bool(run.get("transition_ref"))
    return True
