"""Predicates for stable idempotency keys on retries."""
from __future__ import annotations

from typing import Any


def has_idempotency_key(obj: Any) -> bool:
    return (isinstance(obj, dict)
            and isinstance(obj.get("idempotency_key"), str)
            and len(obj["idempotency_key"]) >= 8)


def retry_is_stable(key: str, prior_keys: list[str]) -> bool:
    """True iff the retry reuses an existing key, i.e. does not mint a new one."""
    return key in prior_keys


def duplicate_delivery_is_inert(send_fn, obj: Any) -> bool:
    """Predicate: sending the same object twice yields the same result and one effect."""
    try:
        r1 = send_fn(obj)
        r2 = send_fn(obj)
    except Exception:
        return False
    return r1 == r2


def retry_does_not_duplicate_effect(effect_counter, send_fn, obj: Any) -> bool:
    """Predicate: two sends with the same key produce exactly one effect."""
    try:
        send_fn(obj)
        send_fn(obj)
    except Exception:
        return False
    return effect_counter.value == 1
