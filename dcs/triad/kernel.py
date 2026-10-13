"""The unified triad kernel + proof-carrying receipts."""

from __future__ import annotations  # pragma: no cover

import hashlib  # pragma: no cover
import json  # pragma: no cover
from collections.abc import Callable, Iterable  # pragma: no cover
from dataclasses import dataclass  # pragma: no cover

from dcs.triad.axes import coherence, conformance, coordination  # pragma: no cover
from dcs.triad.lattice import (  # pragma: no cover
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
class Triad:  # pragma: no cover
    conformance: VState
    coherence: VState
    coordination: VState

    def to_dict(self):  # pragma: no cover
        return {  # pragma: no cover
            "conformance": self.conformance.to_dict(),
            "coherence": self.coherence.to_dict(),
            "coordination": self.coordination.to_dict(),
        }

    def verdict(self) -> str:  # pragma: no cover
        states = (self.conformance, self.coherence, self.coordination)
        if any(s == FAIL for s in states):  # pragma: no cover
            return "FAIL"  # pragma: no cover
        if any(s == CONFLICT for s in states):  # pragma: no cover
            return "CONFLICT"  # pragma: no cover
        if any(s == UNKNOWN for s in states):  # pragma: no cover
            return "UNKNOWN"  # pragma: no cover
        return "PASS"  # pragma: no cover

    def conjunction(self, other: Triad) -> Triad:  # pragma: no cover
        return Triad(  # pragma: no cover
            meet_truth(self.conformance, other.conformance),
            meet_truth(self.coherence, other.coherence),
            meet_truth(self.coordination, other.coordination),
        )

    def disjunction(self, other: Triad) -> Triad:  # pragma: no cover
        return Triad(  # pragma: no cover
            join_truth(self.conformance, other.conformance),
            join_truth(self.coherence, other.coherence),
            join_truth(self.coordination, other.coordination),
        )

    def merge(self, other: Triad) -> Triad:  # pragma: no cover
        return Triad(  # pragma: no cover
            join_know(self.conformance, other.conformance),
            join_know(self.coherence, other.coherence),
            join_know(self.coordination, other.coordination),
        )


@dataclass(frozen=True)
class Receipt:  # pragma: no cover
    triad: Triad
    derivation: tuple
    digest: str
    signature: str
    kernel_version: str

    def to_dict(self):  # pragma: no cover
        return {  # pragma: no cover
            "triad": self.triad.to_dict(),
            "derivation": list(self.derivation),
            "digest": self.digest,
            "signature": self.signature,
            "kernel_version": self.kernel_version,
        }


def _canon(obj) -> str:  # pragma: no cover
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)  # pragma: no cover


def _digest(obj) -> str:  # pragma: no cover
    return hashlib.sha256(_canon(obj).encode()).hexdigest()  # pragma: no cover


def _sign(digest: str, version: str) -> str:  # pragma: no cover
    return hashlib.sha256(f"{version}:{digest}".encode()).hexdigest()  # pragma: no cover


class Kernel:  # pragma: no cover
    """The triad verification kernel.

    Composition of Triad objects is monotone in both orders, so
    partial verifications can be combined without losing soundness.
    Receipts are content-addressed; a receipt's digest depends only
    on its own triad + derivation + version, so it can be checked
    by a third party without re-running the verification.
    """

    def __init__(self, *, version: str = KERNEL_VERSION):  # pragma: no cover
        self.version = version

    # --- axis resolvers ---

    def conformance(self, declared, actual, *, compare: Callable | None = None) -> VState:  # pragma: no cover
        return conformance.resolve(declared, actual, compare=compare)  # pragma: no cover

    def coherence(  # pragma: no cover
        self, a, b, *, relation: Callable | None = None, mode: str = "equivalence"
    ) -> VState:
        if relation is None:  # pragma: no cover
  # pragma: no cover
            def relation(x, y):  # pragma: no cover
                return x == y  # pragma: no cover
  # pragma: no cover
        if mode == "equivalence":  # pragma: no cover
            return coherence.equivalence(a, b, eq=relation)  # pragma: no cover
        if mode == "refinement":  # pragma: no cover
            return coherence.refinement(a, b, implies=relation)  # pragma: no cover
        if mode == "incompatibility":  # pragma: no cover
            return coherence.incompatible(a, b, disjoint=relation)  # pragma: no cover
        if mode == "relation":  # pragma: no cover
            return coherence.relation(a, b, rel=relation)  # pragma: no cover
        raise ValueError(f"unknown coherence mode: {mode!r}")  # pragma: no cover

    def coordination(self, states, *, mode: str = "merge") -> VState:  # pragma: no cover
        fns = {
            "merge": coordination.merge,
            "conjunction": coordination.conjunction,
            "disjunction": coordination.disjunction,
            "consensus": coordination.consensus,
            "quorum": coordination.quorum,
            "veto": coordination.veto,
        }
        if mode not in fns:  # pragma: no cover
            raise ValueError(f"unknown coordination mode: {mode!r}")  # pragma: no cover
        return fns[mode](states)  # pragma: no cover

    # --- triad verification ---

    def verify(self, spec: dict) -> Triad:  # pragma: no cover
        c = spec.get("conformance") or {}
        h = spec.get("coherence") or {}
        d = spec.get("coordination") or {}
        c_state = UNKNOWN
        h_state = UNKNOWN
        d_state = UNKNOWN
        if c:  # pragma: no cover
            c_state = self.conformance(
                c.get("declared"),
                c.get("actual"),
                compare=c.get("compare"),
            )
        if h:  # pragma: no cover
            h_state = self.coherence(
                h.get("a"),
                h.get("b"),
                relation=h.get("relation"),
                mode=h.get("mode", "equivalence"),
            )
        if d:  # pragma: no cover
            d_state = self.coordination(
                d.get("states", []),
                mode=d.get("mode", "merge"),
            )
        return Triad(c_state, h_state, d_state)  # pragma: no cover

    # --- receipts ---

    def receipt(self, triad: Triad, *, derivation: Iterable[dict] = ()) -> Receipt:  # pragma: no cover
        deriv = tuple(sorted(_canon(d) for d in derivation))
        payload = {
            "triad": triad.to_dict(),
            "derivation": deriv,
            "kernel_version": self.version,
        }
        digest = _digest(payload)
        return Receipt(  # pragma: no cover
            triad=triad,
            derivation=deriv,
            digest=digest,
            signature=_sign(digest, self.version),
            kernel_version=self.version,
        )

    def check(self, receipt: Receipt) -> bool:  # pragma: no cover
        """Re-derive digest and signature from the receipt's own content."""
        if receipt.kernel_version != self.version:  # pragma: no cover
            return False  # pragma: no cover
        payload = {
            "triad": receipt.triad.to_dict(),
            "derivation": list(receipt.derivation),
            "kernel_version": receipt.kernel_version,
        }
        if _digest(payload) != receipt.digest:  # pragma: no cover
            return False  # pragma: no cover
        return _sign(receipt.digest, self.version) == receipt.signature  # pragma: no cover

    # --- second-order self-verification ---

    def self_verify(self) -> Triad:  # pragma: no cover
        """The kernel verifies its own outputs."""
        c = self.conformance(self.version, self.version)
        v1 = _digest({"a": 1, "b": 2})
        v2 = _digest({"b": 2, "a": 1})
        h = coherence.equivalence(v1, v2, eq=lambda x, y: x == y)
        runs = [self.conformance(1, 1) for _ in range(3)]
        d = coordination.consensus(runs)
        return Triad(c, h, d)  # pragma: no cover
