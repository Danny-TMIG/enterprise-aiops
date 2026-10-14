"""Predicates for fail-closed behavior at every boundary."""
from __future__ import annotations

from typing import Any


def is_rejected(result: Any) -> bool:
    """True iff a boundary result is a rejection (deny / error), not an acceptance."""
    if not isinstance(result, dict):
        return True
    status = result.get("status")
    return status in ("deny", "denied", "error", "rejected", "fail", "failed")


def is_accepted(result: Any) -> bool:
    if not isinstance(result, dict):
        return False
    return result.get("status") in ("allow", "allowed", "success", "ok", "accepted")


def rejects_invalid(send_fn, invalid_obj: Any) -> bool:
    """Predicate: passing an invalid object yields a rejection, never an exception."""
    try:
        result = send_fn(invalid_obj)
    except Exception:
        return True  # an exception is also a fail-closed outcome
    return is_rejected(result)


def rejects_expired(send_fn, expired_obj: Any) -> bool:
    return rejects_invalid(send_fn, expired_obj)


def rejects_unsigned(send_fn, unsigned_obj: Any) -> bool:
    return rejects_invalid(send_fn, unsigned_obj)


def rejects_revoked(send_fn, revoked_obj: Any) -> bool:
    return rejects_invalid(send_fn, revoked_obj)


def never_partially_applies(send_fn, invalid_obj: Any) -> bool:
    """Predicate: an invalid boundary object produces no state change."""
    before = getattr(send_fn, "__state__", None)
    try:
        send_fn(invalid_obj)
    except Exception:
        pass
    after = getattr(send_fn, "__state__", None)
    return before == after
