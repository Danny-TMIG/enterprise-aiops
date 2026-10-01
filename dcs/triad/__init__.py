"""TRIAD — Conformance × Coherence × Coordination as one algebra.

Every verification resolves to a state in Belnap's FOUR, composed
pointwise across three orthogonal axes. The composition is a
distributive bilattice: commutative, associative, idempotent,
monotone in two orders, distributive. Every result emits a
proof-carrying receipt checkable without re-running the check.
"""

from dcs.triad.kernel import KERNEL_VERSION, Kernel, Receipt, Triad
from dcs.triad.lattice import (
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
    "VState",
    "UNKNOWN",
    "PASS",
    "FAIL",
    "CONFLICT",
    "ALL_STATES",
    "truth_le",
    "know_le",
    "meet_truth",
    "join_truth",
    "meet_know",
    "join_know",
    "Kernel",
    "Triad",
    "Receipt",
    "KERNEL_VERSION",
]
