"""Layer soundness — the four properties that make the three-layer split real.

The layer split is not nominal. It is sound only if these four properties
hold. If any fails, the architecture collapses into a monolith pretending
to be three things.
"""
from __future__ import annotations

from contracts.foundations.primitives import Layer


def separation(actor: Layer, action: str) -> bool:
    """L1: Separation — no layer performs another layer's primitive action."""
    permitted = {
        Layer.COGNITION: {"propose", "retrieve", "reason", "plan", "evaluate"},
        Layer.GOVERN: {"authorize", "policy_evaluate", "flow_decide", "approve", "revoke"},
        Layer.COMPUTE: {"execute", "schedule", "observe", "return_evidence"},
    }
    return action in permitted.get(actor, set())


def totality(actors: list[Layer]) -> bool:
    """L2: Totality — the three layers cover every permitted action."""
    return set(actors) == {Layer.COGNITION, Layer.GOVERN, Layer.COMPUTE}


def non_amplification(parent: Layer, child: Layer, action: str) -> bool:
    """L3: Non-amplification — a downstream layer cannot widen an upstream decision."""
    order = [Layer.COGNITION, Layer.GOVERN, Layer.COMPUTE]
    if order.index(child) <= order.index(parent):
        return True
    return action in ("realize", "observe", "return_evidence", "fail", "abstain")


def authority_conservation(before: set[str], after: set[str]) -> bool:
    """L4: Authority conservation — no transition creates authority from nothing."""
    return after.issubset(before) or before.issuperset(after)
