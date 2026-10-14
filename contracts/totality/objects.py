"""Totality of the object space.

Every object that crosses a boundary must be named in exactly one of the
boundary contract categories. An unnamed object cannot legally cross a
boundary.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundaryObject:
    name: str
    category: str
    direction: str  # "request", "result", "control", "envelope"


CATEGORIES = (
    "authority",
    "information",
    "capabilities",
    "execution",
    "closure",
    "control",
    "envelope",
)

OBJECTS: tuple[BoundaryObject, ...] = (
    BoundaryObject("CommonEnvelope", "envelope", "envelope"),

    BoundaryObject("AuthorizationRequest", "authority", "request"),
    BoundaryObject("AuthorizationDecision", "authority", "result"),

    BoundaryObject("InformationFlowRequest", "information", "request"),
    BoundaryObject("InformationFlowDecision", "information", "result"),
    BoundaryObject("GovernedKnowledgeResult", "information", "result"),

    BoundaryObject("CapabilityRequest", "capabilities", "request"),
    BoundaryObject("GovernedCapabilitySet", "capabilities", "result"),

    BoundaryObject("ExecutionOrder", "execution", "request"),
    BoundaryObject("ExecutionStatus", "execution", "result"),
    BoundaryObject("ExecutionResult", "execution", "result"),
    BoundaryObject("ExecutionEvidence", "execution", "result"),

    BoundaryObject("GovernedOutcome", "closure", "result"),
    BoundaryObject("CognitiveStateUpdateDirective", "closure", "result"),

    BoundaryObject("ApprovalRequest", "control", "control"),
    BoundaryObject("CancellationRevocationDirective", "control", "control"),
    BoundaryObject("ASFError", "control", "control"),
)


def in_category(cat: str) -> list[BoundaryObject]:
    return [o for o in OBJECTS if o.category == cat]


def names() -> set[str]:
    return {o.name for o in OBJECTS}


def categories_of(name: str) -> list[str]:
    return [o.category for o in OBJECTS if o.name == name]
