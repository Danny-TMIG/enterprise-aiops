"""Predicates for classification and information flow."""
from __future__ import annotations

from typing import Any

# Lattice: unclassified < internal < confidential < secret
LATTICE = {"unclassified": 0, "internal": 1, "confidential": 2, "secret": 3}


def no_downgrade(original: str, result: str) -> bool:
    """Transformation cannot reduce a classification."""
    return LATTICE.get(result, 99) >= LATTICE.get(original, 0)


def release_is_authorized(request: dict[str, Any], decision: dict[str, Any]) -> bool:
    return (isinstance(request, dict)
            and isinstance(decision, dict)
            and decision.get("status") == "allow"
            and decision.get("request_id") == request.get("object_id"))


def representation_is_least_disclosing(release: dict[str, Any], requested_class: str) -> bool:
    """Predicate: the released representation is no more permissive than the request allows."""
    if not isinstance(release, dict):
        return False
    released_class = release.get("representation_class")
    order = ("denied", "metadata_only", "provenance_only", "aggregated", "redacted",
             "anonymized", "abstracted", "derived", "full")
    try:
        return order.index(released_class) <= order.index(requested_class)
    except ValueError:
        return False
