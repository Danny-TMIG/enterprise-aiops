"""TRIAD — Conformance × Coherence × Coordination as one algebra.

Every verification resolves to a state in Belnap's FOUR, composed
pointwise across three orthogonal axes. The composition is a
distributive bilattice: commutative, associative, idempotent,
monotone in two orders, distributive. Every result emits a
proof-carrying receipt checkable without re-running the check.
"""

from dcs.triad.kernel import KERNEL_VERSION, Kernel, Receipt, Triad  # pragma: no cover
from dcs.triad.lattice import (  # pragma: no cover
    ALL_STATES,
    CONFLICT,
    FAIL,
    PASS,
    UNKNOWN,
    VState,
    join_know,
    join_truth,
    know_le,
    meet_know,
    meet_truth,
    truth_le,
)

__all__ = [
    "ALL_STATES",
    "CONFLICT",
    "FAIL",
    "KERNEL_VERSION",
    "PASS",
    "UNKNOWN",
    "Kernel",
    "Receipt",
    "Triad",
    "VState",
    "join_know",
    "join_truth",
    "know_le",
    "meet_know",
    "meet_truth",
    "truth_le",
]
