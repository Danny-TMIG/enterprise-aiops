"""ASF primitives — the irreducible types from which everything else is built.

A primitive is a definition. It has no interior structure to prove; it is
the vocabulary the system speaks. Every predicate and invariant is stated
over these types.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Layer(str, Enum):
    """The three ASF layers. Exhaustive."""
    COGNITION = "cognition"
    GOVERN = "govern"
    COMPUTE = "compute"


class Outcome(str, Enum):
    """The five governance decision outcomes. Exhaustive."""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    ESCALATE = "escalate"
    INDETERMINATE = "indeterminate"


class Classification(str, Enum):
    """The classification lattice. Ordered."""
    UNCLASSIFIED = "unclassified"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


class RepresentationClass(str, Enum):
    """Liquid Aperture release classes. Ordered by disclosure."""
    DENIED = "denied"
    METADATA_ONLY = "metadata_only"
    PROVENANCE_ONLY = "provenance_only"
    AGGREGATED = "aggregated"
    REDACTED = "redacted"
    ANONYMIZED = "anonymized"
    ABSTRACTED = "abstracted"
    DERIVED = "derived"
    FULL = "full"


@dataclass(frozen=True)
class Identity:
    """An identity is a durable reference, not a credential."""
    principal_id: str
    sovereign_domain: str


@dataclass(frozen=True)
class Authority:
    """Authority is a bounded, attributable, time-aware, revocable grant."""
    subject: Identity
    action: str
    object_id: str
    purpose: str
    valid_until: str
    delegable: bool = False


@dataclass(frozen=True)
class Object:
    """A governed object is any addressable thing an authority ranges over."""
    object_id: str
    classification: Classification


@dataclass(frozen=True)
class Evidence:
    """Evidence is a typed claim with a source. Not automatically true."""
    claim: str
    source: str
    integrity: str


@dataclass(frozen=True)
class Capability:
    """A capability is a named function that Compute can realize if authorized."""
    capability_id: str
    provider_id: str


@dataclass(frozen=True)
class Order:
    """An ExecutionOrder is the sole Govern -> Compute command."""
    order_id: str
    capability: Capability
    subject: Identity
    max_quantity: int
    evidence_obligations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Run:
    """A run is a bounded execution instance with a lifecycle."""
    run_id: str
    order_id: str
    status: str
    evidence_refs: list[str] = field(default_factory=list)
