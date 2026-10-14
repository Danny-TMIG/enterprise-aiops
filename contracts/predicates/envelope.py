"""Predicates for the ASF Common Envelope (all boundary objects)."""
from __future__ import annotations

from typing import Any

REQUIRED_FIELDS = (
    "schema_version",
    "object_id",
    "correlation_id",
    "causation_id",
    "sovereign_domain",
    "purpose",
    "classification",
    "issued_at",
    "integrity",
    "evidence_refs",
)


def is_envelope(obj: Any) -> bool:
    """True iff obj is a dict carrying every required Common Envelope field."""
    if not isinstance(obj, dict):
        return False
    return all(k in obj for k in REQUIRED_FIELDS)


def has_correlation(obj: Any) -> bool:
    return isinstance(obj, dict) and isinstance(obj.get("correlation_id"), str) and obj["correlation_id"]


def has_causation(obj: Any) -> bool:
    return isinstance(obj, dict) and isinstance(obj.get("causation_id"), str)


def has_validity_window(obj: Any) -> bool:
    return (isinstance(obj, dict)
            and "issued_at" in obj
            and "valid_until" in obj
            and obj["issued_at"] <= obj["valid_until"])


def is_expired(obj: Any, now: str) -> bool:
    """True iff the object's validity window has passed."""
    return isinstance(obj, dict) and isinstance(obj.get("valid_until"), str) and obj["valid_until"] < now


def has_integrity(obj: Any) -> bool:
    return isinstance(obj, dict) and isinstance(obj.get("integrity"), str) and len(obj["integrity"]) >= 16


def carries_classification(obj: Any) -> bool:
    return isinstance(obj, dict) and isinstance(obj.get("classification"), str) and obj["classification"]
