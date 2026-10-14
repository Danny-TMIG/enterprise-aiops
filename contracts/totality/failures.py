"""Totality of the failure space.

Every failure that can occur must fall into exactly one class, and each
class has exactly one required response. An unclassified failure is a
system-level bug: the system does not know what to do.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureClass:
    name: str
    examples: tuple[str, ...]
    required_response: str


CLASSES: tuple[FailureClass, ...] = (
    FailureClass(
        name="input",
        examples=("malformed", "injection", "ambiguous", "missing provenance"),
        required_response="reject, clarify, sanitize, or contain",
    ),
    FailureClass(
        name="state",
        examples=("stale base", "conflict", "corruption", "poisoned memory"),
        required_response="stop mutation, quarantine affected versions, recover or escalate",
    ),
    FailureClass(
        name="knowledge",
        examples=("denied", "revoked", "stale", "unavailable", "substituted"),
        required_response="return visible outcome; never bypass Govern",
    ),
    FailureClass(
        name="substrate",
        examples=("crash", "incompatibility", "unsafe output", "contradiction"),
        required_response="retry, substitute within eligibility, degrade, abstain, or terminate",
    ),
    FailureClass(
        name="dependency",
        examples=("Govern decision unavailable", "execution failure", "revoked order"),
        required_response="wait, cancel, fail, or recover under the governed outcome",
    ),
    FailureClass(
        name="evidence",
        examples=("missing", "fabricated", "inconsistent", "expired", "over-disclosing"),
        required_response="mark incomplete or disputed, contain, supersede, or withhold release",
    ),
)


def classify(example: str) -> FailureClass | None:
    """Return the unique class an example belongs to, or None if unclassified."""
    for cls in CLASSES:
        if example in cls.examples:
            return cls
    return None


def all_examples() -> set[str]:
    out: set[str] = set()
    for cls in CLASSES:
        out.update(cls.examples)
    return out
