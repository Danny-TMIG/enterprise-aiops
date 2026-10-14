"""Totality of the action space.

Every action a component can perform must be classified into exactly one
of a small, exhaustive set. An action that is not classified is a gap: the
system does not know who owns it.

This module enumerates the complete action vocabulary and assigns each
action to exactly one owning layer. If you add a new action and do not
assign it here, tests/test_totality.py::test_all_actions_classified fails.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from contracts.foundations.primitives import Layer


class ActionKind(str, Enum):
    """The atomic verbs the system recognizes."""
    # Cognition
    PROPOSE = "propose"
    RETRIEVE = "retrieve"
    REASON = "reason"
    PLAN = "plan"
    EVALUATE = "evaluate"
    FORM_REPRESENTATION = "form_representation"
    RESOLVE_STATE = "resolve_state"
    GROUND = "ground"
    ROUTE = "route"
    RESPOND = "respond"
    # Govern
    AUTHORIZE = "authorize"
    DENY = "deny"
    CONDITIONALIZE = "conditionalize"
    ESCALATE = "escalate"
    CLASSIFY = "classify"
    DECIDE_FLOW = "decide_flow"
    DECIDE_POLICY = "decide_policy"
    APPROVE = "approve"
    REVOKE = "revoke"
    CANCEL = "cancel"
    RESOLVE_CAPABILITY = "resolve_capability"
    ISSUE_ORDER = "issue_order"
    CORRELATE_EVIDENCE = "correlate_evidence"
    VERIFY_OUTCOME = "verify_outcome"
    # Compute
    QUALIFY = "qualify"
    REALIZE = "realize"
    SCHEDULE = "schedule"
    EXECUTE = "execute"
    OBSERVE = "observe"
    RETURN_EVIDENCE = "return_evidence"
    CHECKPOINT = "checkpoint"
    RECOVER = "recover"
    # Cross-layer
    ABSTAIN = "abstain"
    FAIL = "fail"
    DEGRADE = "degrade"
    CONTAIN = "contain"


@dataclass(frozen=True)
class ActionAssignment:
    action: ActionKind
    owner: Layer
    note: str = ""


# The complete assignment. Every ActionKind appears exactly once.
# test_totality checks both directions: no action unassigned, no assignment stale.
ASSIGNMENTS: tuple[ActionAssignment, ...] = (
    ActionAssignment(ActionKind.PROPOSE, Layer.COGNITION),
    ActionAssignment(ActionKind.RETRIEVE, Layer.COGNITION),
    ActionAssignment(ActionKind.REASON, Layer.COGNITION),
    ActionAssignment(ActionKind.PLAN, Layer.COGNITION),
    ActionAssignment(ActionKind.EVALUATE, Layer.COGNITION),
    ActionAssignment(ActionKind.FORM_REPRESENTATION, Layer.COGNITION),
    ActionAssignment(ActionKind.RESOLVE_STATE, Layer.COGNITION),
    ActionAssignment(ActionKind.GROUND, Layer.COGNITION),
    ActionAssignment(ActionKind.ROUTE, Layer.COGNITION),
    ActionAssignment(ActionKind.RESPOND, Layer.COGNITION),

    ActionAssignment(ActionKind.AUTHORIZE, Layer.GOVERN),
    ActionAssignment(ActionKind.DENY, Layer.GOVERN),
    ActionAssignment(ActionKind.CONDITIONALIZE, Layer.GOVERN),
    ActionAssignment(ActionKind.ESCALATE, Layer.GOVERN),
    ActionAssignment(ActionKind.CLASSIFY, Layer.GOVERN),
    ActionAssignment(ActionKind.DECIDE_FLOW, Layer.GOVERN),
    ActionAssignment(ActionKind.DECIDE_POLICY, Layer.GOVERN),
    ActionAssignment(ActionKind.APPROVE, Layer.GOVERN),
    ActionAssignment(ActionKind.REVOKE, Layer.GOVERN),
    ActionAssignment(ActionKind.CANCEL, Layer.GOVERN),
    ActionAssignment(ActionKind.RESOLVE_CAPABILITY, Layer.GOVERN),
    ActionAssignment(ActionKind.ISSUE_ORDER, Layer.GOVERN),
    ActionAssignment(ActionKind.CORRELATE_EVIDENCE, Layer.GOVERN),
    ActionAssignment(ActionKind.VERIFY_OUTCOME, Layer.GOVERN),

    ActionAssignment(ActionKind.QUALIFY, Layer.COMPUTE),
    ActionAssignment(ActionKind.REALIZE, Layer.COMPUTE),
    ActionAssignment(ActionKind.SCHEDULE, Layer.COMPUTE),
    ActionAssignment(ActionKind.EXECUTE, Layer.COMPUTE),
    ActionAssignment(ActionKind.OBSERVE, Layer.COMPUTE),
    ActionAssignment(ActionKind.RETURN_EVIDENCE, Layer.COMPUTE),
    ActionAssignment(ActionKind.CHECKPOINT, Layer.COMPUTE),
    ActionAssignment(ActionKind.RECOVER, Layer.COMPUTE),

    ActionAssignment(ActionKind.ABSTAIN, Layer.GOVERN,
                     "Abstention is a Govern decision outcome, not a Cognition failure"),
    ActionAssignment(ActionKind.FAIL, Layer.GOVERN,
                     "Failure is reported through Govern's correlation path"),
    ActionAssignment(ActionKind.DEGRADE, Layer.GOVERN,
                     "Degradation is a Govern decision, not an implicit Compute substitution"),
    ActionAssignment(ActionKind.CONTAIN, Layer.GOVERN,
                     "Containment is a Govern response to a security event"),
)


def owner_of(action: ActionKind) -> Layer | None:
    for a in ASSIGNMENTS:
        if a.action == action:
            return a.owner
    return None


def actions_of(layer: Layer) -> list[ActionKind]:
    return [a.action for a in ASSIGNMENTS if a.owner == layer]
