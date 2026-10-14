"""Predicates for authority boundaries (GOV-INV-001..003)."""
from __future__ import annotations

from typing import Any


def cognition_cannot_authorize(actor_layer: str, action: str) -> bool:
    """GOV-INV-001: Cognition cannot authorize its own consequential action."""
    return not (actor_layer == "cognition" and action == "authorize")


def govern_cannot_execute(actor_layer: str, action: str) -> bool:
    """GOV-INV-002: Govern cannot execute a physical workload."""
    return not (actor_layer == "govern" and action == "execute")


def compute_cannot_broaden(original: dict[str, Any], executed: dict[str, Any]) -> bool:
    """GOV-INV-003: Compute cannot broaden an order or substitute a capability."""
    if not isinstance(original, dict) or not isinstance(executed, dict):
        return False
    for key in ("capability_id", "provider_id", "order_id", "subject"):
        if key in original and key in executed and original[key] != executed[key]:
            return False
    if "max_quantity" in original and "max_quantity" in executed:
        if executed["max_quantity"] > original["max_quantity"]:
            return False
    return True


def delegation_does_not_amplify(parent: dict[str, Any], child: dict[str, Any]) -> bool:
    """A delegated grant may not exceed its parent's authority."""
    if not isinstance(parent, dict) or not isinstance(child, dict):
        return False
    for key in ("subject", "action", "object", "sovereign_domain"):
        if parent.get(key) is not None and child.get(key) != parent.get(key):
            return False
    p_exp = parent.get("valid_until")
    c_exp = child.get("valid_until")
    if isinstance(p_exp, str) and isinstance(c_exp, str) and c_exp > p_exp:
        return False
    return True


def revocation_blocks_new_orders(revoked: set[str], order_subject: str) -> bool:
    return order_subject not in revoked
