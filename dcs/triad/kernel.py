"""The unified triad kernel + proof-carrying receipts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from dcs.triad.axes import coherence, conformance, coordination
from dcs.triad.lattice import (
    CONFLICT,
    FAIL,
    UNKNOWN,
    VState,
    join_know,
    join_truth,
    meet_truth,
)

KERNEL_VERSION = "triad-0.1.0"


@dataclass(frozen=True)
class Triad:
    conformance: VState
    coherence: VState
    coordination: VState

    def to_dict(self):
        return {
            "conformance": self.conformance.to_dict(),
            "coherence": self.coherence.to_dict(),
            "coordination": self.coordination.to_dict(),
        }

    def verdict(self) -> str:
        states = (self.conformance, self.coherence, self.coordination)
        if any(s == FAIL for s in states):
            return "FAIL"
        if any(s == CONFLICT for s in states):
            return "CONFLICT"
        if any(s == UNKNOWN for s in states):
            return "UNKNOWN"
        return "PASS"

    def conjunction(self, other: Triad) -> Triad:
        return Triad(
            meet_truth(self.conformance, other.conformance),
            meet_truth(self.coherence, other.coherence),
            meet_truth(self.coordination, other.coordination),
        )

    def disjunction(self, other: Triad) -> Triad:
        return Triad(
            join_truth(self.conformance, other.conformance),
            join_truth(self.coherence, other.coherence),
            join_truth(self.coordination, other.coordination),
        )

    def merge(self, other: Triad) -> Triad:
        return Triad(
            join_know(self.conformance, other.conformance),
            join_know(self.coherence, other.coherence),
            join_know(self.coordination, other.coordination),
        )


@dataclass(frozen=True)
class Receipt:
    triad: Triad
    derivation: tuple
    digest: str
    signature: str
    kernel_version: str

    def to_dict(self):
        return {
            "triad": self.triad.to_dict(),
            "derivation": list(self.derivation),
            "digest": self.digest,
            "signature": self.signature,
            "kernel_version": self.kernel_version,
        }


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _digest(obj) -> str:
    return hashlib.sha256(_canon(obj).encode()).hexdigest()


def _sign(digest: str, version: str) -> str:
    return hashlib.sha256(f"{version}:{digest}".encode()).hexdigest()


class Kernel:
    """The triad verification kernel.

    Composition of Triad objects is monotone in both orders, so
    partial verifications can be combined without losing soundness.
    Receipts are content-addressed; a receipt's digest depends only
    on its own triad + derivation + version, so it can be checked
    by a third party without re-running the verification.
    """

    def __init__(self, *, version: str = KERNEL_VERSION):
        self.version = version

    # --- axis resolvers ---

    def conformance(self, declared, actual, *, compare: Callable | None = None) -> VState:
        return conformance.resolve(declared, actual, compare=compare)

    def coherence(
        self, a, b, *, relation: Callable | None = None, mode: str = "equivalence"
    ) -> VState:
        if relation is None:

            def relation(x, y):  # noqa: E731
                return x == y

        if mode == "equivalence":
            return coherence.equivalence(a, b, eq=relation)
        if mode == "refinement":
            return coherence.refinement(a, b, implies=relation)
        if mode == "incompatibility":
            return coherence.incompatible(a, b, disjoint=relation)
        if mode == "relation":
            return coherence.relation(a, b, rel=relation)
        raise ValueError(f"unknown coherence mode: {mode!r}")

    def coordination(self, states, *, mode: str = "merge") -> VState:
        fns = {
            "merge": coordination.merge,
            "conjunction": coordination.conjunction,
            "disjunction": coordination.disjunction,
            "consensus": coordination.consensus,
            "quorum": coordination.quorum,
            "veto": coordination.veto,
        }
        if mode not in fns:
            raise ValueError(f"unknown coordination mode: {mode!r}")
        return fns[mode](states)

    # --- triad verification ---

    def verify(self, spec: dict) -> Triad:
        c = spec.get("conformance") or {}
        h = spec.get("coherence") or {}
        d = spec.get("coordination") or {}
        c_state = UNKNOWN
        h_state = UNKNOWN
        d_state = UNKNOWN
        if c:
            c_state = self.conformance(
                c.get("declared"),
                c.get("actual"),
                compare=c.get("compare"),
            )
        if h:
            h_state = self.coherence(
                h.get("a"),
                h.get("b"),
                relation=h.get("relation"),
                mode=h.get("mode", "equivalence"),
            )
        if d:
            d_state = self.coordination(
                d.get("states", []),
                mode=d.get("mode", "merge"),
            )
        return Triad(c_state, h_state, d_state)

    # --- receipts ---

    def receipt(self, triad: Triad, *, derivation: Iterable[dict] = ()) -> Receipt:
        deriv = tuple(sorted(_canon(d) for d in derivation))
        payload = {
            "triad": triad.to_dict(),
            "derivation": deriv,
            "kernel_version": self.version,
        }
        digest = _digest(payload)
        return Receipt(
            triad=triad,
            derivation=deriv,
            digest=digest,
            signature=_sign(digest, self.version),
            kernel_version=self.version,
        )

    def check(self, receipt: Receipt) -> bool:
        """Re-derive digest and signature from the receipt's own content."""
        if receipt.kernel_version != self.version:
            return False
        payload = {
            "triad": receipt.triad.to_dict(),
            "derivation": list(receipt.derivation),
            "kernel_version": receipt.kernel_version,
        }
        if _digest(payload) != receipt.digest:
            return False
        return _sign(receipt.digest, self.version) == receipt.signature

    # --- second-order self-verification ---

    def self_verify(self) -> Triad:
        """The kernel verifies its own outputs."""
        c = self.conformance(self.version, self.version)
        v1 = _digest({"a": 1, "b": 2})
        v2 = _digest({"b": 2, "a": 1})
        h = coherence.equivalence(v1, v2, eq=lambda x, y: x == y)
        runs = [self.conformance(1, 1) for _ in range(3)]
        d = coordination.consensus(runs)
        return Triad(c, h, d)
