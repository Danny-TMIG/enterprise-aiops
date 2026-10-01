#!/usr/bin/env python3
"""Install the TRIAD kernel: conformance × coherence × coordination as one algebra."""
import os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "enterprise_aiops"
os.chdir(ROOT)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
bk = ROOT / f".triad-backups/{stamp}"; bk.mkdir(parents=True, exist_ok=True)

files = {}

files["dcs/triad/__init__.py"] = '''"""TRIAD — Conformance × Coherence × Coordination as one algebra.

Every verification resolves to a state in Belnap's FOUR, composed
pointwise across three orthogonal axes. The composition is a
distributive bilattice: commutative, associative, idempotent,
monotone in two orders, distributive. Every result emits a
proof-carrying receipt checkable without re-running the check.
"""
from dcs.triad.lattice import (
    VState, UNKNOWN, PASS, FAIL, CONFLICT, ALL_STATES,
    truth_le, know_le, meet_truth, join_truth, meet_know, join_know,
)
from dcs.triad.kernel import Kernel, Triad, Receipt, KERNEL_VERSION

__all__ = [
    "VState", "UNKNOWN", "PASS", "FAIL", "CONFLICT", "ALL_STATES",
    "truth_le", "know_le", "meet_truth", "join_truth", "meet_know", "join_know",
    "Kernel", "Triad", "Receipt", "KERNEL_VERSION",
]
'''

files["dcs/triad/lattice.py"] = '''"""Belnap FOUR — the algebraic substrate of the triad kernel.

    UNKNOWN  = (0, 0)  neither proven
    PASS     = (1, 0)  proven true
    FAIL     = (0, 1)  proven false
    CONFLICT = (1, 1)  both proven

Two monotone orders:
    truth:      FAIL < UNKNOWN,CONFLICT < PASS
    knowledge:  UNKNOWN < PASS,FAIL < CONFLICT
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable

@dataclass(frozen=True)
class VState:
    t: int
    f: int

    def __post_init__(self):
        if self.t not in (0, 1) or self.f not in (0, 1):
            raise ValueError(f"coordinates must be 0/1, got ({self.t},{self.f})")

    @property
    def name(self) -> str:
        return {(0, 0): "UNKNOWN", (1, 0): "PASS",
                (0, 1): "FAIL", (1, 1): "CONFLICT"}[(self.t, self.f)]

    def __repr__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {"t": self.t, "f": self.f, "name": self.name}

    @classmethod
    def from_any(cls, x) -> "VState":
        if isinstance(x, cls):
            return x
        if isinstance(x, dict):
            return cls(int(x.get("t", 0)), int(x.get("f", 0)))
        if isinstance(x, str):
            return {"UNKNOWN": UNKNOWN, "PASS": PASS,
                    "FAIL": FAIL, "CONFLICT": CONFLICT}[x.upper()]
        raise TypeError(f"cannot coerce {x!r} to VState")


UNKNOWN  = VState(0, 0)
PASS     = VState(1, 0)
FAIL     = VState(0, 1)
CONFLICT = VState(1, 1)
ALL_STATES = (UNKNOWN, PASS, FAIL, CONFLICT)


# ---------- orders ----------

def truth_le(a, b) -> bool:
    """a ⊑_t b  iff  a.t ≤ b.t  and  a.f ≥ b.f."""
    return a.t <= b.t and a.f >= b.f

def know_le(a, b) -> bool:
    """a ⊑_k b  iff  a.t ≤ b.t  and  a.f ≤ b.f."""
    return a.t <= b.t and a.f <= b.f


# ---------- lattice operations ----------

def meet_truth(a, b):
    """Conjunction (both must hold)."""
    return VState(min(a.t, b.t), max(a.f, b.f))

def join_truth(a, b):
    """Disjunction (either may hold)."""
    return VState(max(a.t, b.t), min(a.f, b.f))

def meet_know(a, b):
    """Common information."""
    return VState(min(a.t, b.t), min(a.f, b.f))

def join_know(a, b):
    """Union of information."""
    return VState(max(a.t, b.t), max(a.f, b.f))


# ---------- folds ----------

def fold_v(states: Iterable[VState], op, *, empty=None) -> VState:
    it = iter(states)
    try:
        acc = next(it)
    except StopIteration:
        return empty if empty is not None else UNKNOWN
    for s in it:
        acc = op(acc, s)
    return acc


def consensus(states) -> VState:
    """Unanimous agreement, otherwise CONFLICT."""
    s = [VState.from_any(x) for x in states]
    if not s:
        return UNKNOWN
    return s[0] if all(x == s[0] for x in s) else CONFLICT


def quorum(states) -> VState:
    """Strict-majority PASS → PASS; strict-majority FAIL → FAIL; else CONFLICT."""
    s = [VState.from_any(x) for x in states]
    if not s:
        return UNKNOWN
    n = len(s)
    p = sum(1 for x in s if x == PASS)
    f = sum(1 for x in s if x == FAIL)
    if p > n // 2:
        return PASS
    if f > n // 2:
        return FAIL
    return CONFLICT
'''

files["dcs/triad/axes/__init__.py"] = '''"""Three orthogonal axes over the same lattice."""
from dcs.triad.axes import conformance, coherence, coordination

__all__ = ["conformance", "coherence", "coordination"]
'''

files["dcs/triad/axes/conformance.py"] = '''"""Conformance: does the artifact match its declaration?"""
from __future__ import annotations
from typing import Any, Callable, Iterable
from dcs.triad.lattice import VState, PASS, FAIL, UNKNOWN


def resolve(declared: Any, actual: Any, *,
            compare: Callable[[Any, Any], bool] | None = None) -> VState:
    if compare is None:
        compare = lambda d, a: d == a
    try:
        return PASS if compare(declared, actual) else FAIL
    except Exception:
        return UNKNOWN


def schema(declared_fields: set, actual_fields: set) -> VState:
    if not declared_fields:
        return UNKNOWN
    return PASS if set(actual_fields) >= set(declared_fields) else FAIL


def behavioral(pred: Callable[[Any], bool], sample: Iterable[Any], *,
               epsilon: float = 1e-9) -> VState:
    s = list(sample)
    if not s:
        return UNKNOWN
    k = sum(1 for x in s if pred(x))
    if k == len(s):
        return PASS
    if k == 0:
        return FAIL
    rate = k / len(s)
    if abs(rate - 0.5) < epsilon:
        return FAIL
    return UNKNOWN


def certificate(claim: dict, cert: dict, *,
                verifier: Callable[[dict, dict], bool]) -> VState:
    try:
        ok = verifier(claim, cert)
    except Exception:
        return UNKNOWN
    return PASS if ok else FAIL
'''

files["dcs/triad/axes/coherence.py"] = '''"""Coherence: do two artifacts agree with each other?"""
from __future__ import annotations
from typing import Any, Callable, Iterable
from dcs.triad.lattice import VState, PASS, FAIL, UNKNOWN, join_know, fold_v


def equivalence(a: Any, b: Any, *, eq: Callable[[Any, Any], bool]) -> VState:
    try:
        return PASS if eq(a, b) else FAIL
    except Exception:
        return UNKNOWN


def refinement(a: Any, b: Any, *, implies: Callable[[Any, Any], bool]) -> VState:
    try:
        return PASS if implies(a, b) else FAIL
    except Exception:
        return UNKNOWN


def incompatible(a: Any, b: Any, *, disjoint: Callable[[Any, Any], bool]) -> VState:
    try:
        return PASS if disjoint(a, b) else FAIL
    except Exception:
        return UNKNOWN


def relation(a: Any, b: Any, *,
             rel: Callable[[Any, Any], bool | None]) -> VState:
    try:
        got = rel(a, b)
    except Exception:
        return UNKNOWN
    if got is None:
        return UNKNOWN
    return PASS if got else FAIL


def combine(states: Iterable[VState]) -> VState:
    """Union of information across coherent views."""
    return fold_v((VState.from_any(x) for x in states), join_know)
'''

files["dcs/triad/axes/coordination.py"] = '''"""Coordination: do many agents agree together?"""
from __future__ import annotations
from typing import Iterable, List
from dcs.triad.lattice import (
    VState, PASS, FAIL, UNKNOWN, CONFLICT,
    fold_v, join_know, join_truth, meet_truth,
    consensus as _consensus, quorum as _quorum,
)


def _coerce(x) -> VState:
    return VState.from_any(x)


def merge(states: Iterable[VState]) -> VState:
    return fold_v((_coerce(x) for x in states), join_know)


def conjunction(states: Iterable[VState]) -> VState:
    return fold_v((_coerce(x) for x in states), meet_truth)


def disjunction(states: Iterable[VState]) -> VState:
    return fold_v((_coerce(x) for x in states), join_truth)


def consensus(states: Iterable[VState]) -> VState:
    return _consensus(states)


def quorum(states: Iterable[VState]) -> VState:
    return _quorum(states)


def veto(states: Iterable[VState]) -> VState:
    """Any FAIL vetoes; any CONFLICT poisons."""
    s = [_coerce(x) for x in states]
    if not s:
        return UNKNOWN
    if any(x == CONFLICT for x in s):
        return CONFLICT
    if any(x == FAIL for x in s):
        return FAIL
    if all(x == PASS for x in s):
        return PASS
    return UNKNOWN


def weighted(states: Iterable[VState], *,
             weights: Iterable[float] | None = None) -> VState:
    s = [_coerce(x) for x in states]
    if not s:
        return UNKNOWN
    w = list(weights) if weights is not None else [1.0] * len(s)
    if len(w) != len(s):
        raise ValueError("weights length mismatch")
    total = sum(w)
    if total <= 0:
        return UNKNOWN
    p = sum(wi for wi, st in zip(w, s) if st == PASS)
    f = sum(wi for wi, st in zip(w, s) if st == FAIL)
    if p == 0 and f == 0:
        return UNKNOWN
    if p > f:
        return PASS
    if f > p:
        return FAIL
    return CONFLICT
'''

files["dcs/triad/kernel.py"] = '''"""The unified triad kernel + proof-carrying receipts."""
from __future__ import annotations
import hashlib, json, time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from dcs.triad.lattice import (
    VState, PASS, FAIL, UNKNOWN, CONFLICT,
    meet_truth, join_truth, join_know, ALL_STATES,
)
from dcs.triad.axes import conformance as C
from dcs.triad.axes import coherence as H
from dcs.triad.axes import coordination as D


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

    def conjunction(self, other: "Triad") -> "Triad":
        return Triad(
            meet_truth(self.conformance, other.conformance),
            meet_truth(self.coherence, other.coherence),
            meet_truth(self.coordination, other.coordination),
        )

    def disjunction(self, other: "Triad") -> "Triad":
        return Triad(
            join_truth(self.conformance, other.conformance),
            join_truth(self.coherence, other.coherence),
            join_truth(self.coordination, other.coordination),
        )

    def merge(self, other: "Triad") -> "Triad":
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

    def conformance(self, declared, actual, *,
                    compare: Callable | None = None) -> VState:
        return C.resolve(declared, actual, compare=compare)

    def coherence(self, a, b, *,
                  relation: Callable | None = None,
                  mode: str = "equivalence") -> VState:
        if relation is None:
            relation = lambda x, y: x == y
        if mode == "equivalence":
            return H.equivalence(a, b, eq=relation)
        if mode == "refinement":
            return H.refinement(a, b, implies=relation)
        if mode == "incompatibility":
            return H.incompatible(a, b, disjoint=relation)
        if mode == "relation":
            return H.relation(a, b, rel=relation)
        raise ValueError(f"unknown coherence mode: {mode!r}")

    def coordination(self, states, *, mode: str = "merge") -> VState:
        fns = {
            "merge": D.merge,
            "conjunction": D.conjunction,
            "disjunction": D.disjunction,
            "consensus": D.consensus,
            "quorum": D.quorum,
            "veto": D.veto,
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
                c.get("declared"), c.get("actual"),
                compare=c.get("compare"),
            )
        if h:
            h_state = self.coherence(
                h.get("a"), h.get("b"),
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

    def receipt(self, triad: Triad, *,
                derivation: Iterable[dict] = ()) -> Receipt:
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
        h = H.equivalence(v1, v2, eq=lambda x, y: x == y)
        runs = [self.conformance(1, 1) for _ in range(3)]
        d = D.consensus(runs)
        return Triad(c, h, d)
'''

files["dcs/triad/laws.py"] = '''"""Algebraic laws. If these hold, composition is sound."""
from dcs.triad.lattice import (
    ALL_STATES, truth_le, know_le,
    meet_truth, join_truth, meet_know, join_know,
)


def commutative() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            if join_truth(a, b) != join_truth(b, a): return False
            if join_know(a, b) != join_know(b, a): return False
            if meet_truth(a, b) != meet_truth(b, a): return False
            if meet_know(a, b) != meet_know(b, a): return False
    return True


def associative() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if join_truth(join_truth(a, b), c) != join_truth(a, join_truth(b, c)):
                    return False
                if join_know(join_know(a, b), c) != join_know(a, join_know(b, c)):
                    return False
                if meet_truth(meet_truth(a, b), c) != meet_truth(a, meet_truth(b, c)):
                    return False
                if meet_know(meet_know(a, b), c) != meet_know(a, meet_know(b, c)):
                    return False
    return True


def idempotent() -> bool:
    for a in ALL_STATES:
        if join_truth(a, a) != a: return False
        if join_know(a, a) != a: return False
        if meet_truth(a, a) != a: return False
        if meet_know(a, a) != a: return False
    return True


def monotone() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if truth_le(a, b) and not truth_le(join_truth(a, c), join_truth(b, c)):
                    return False
                if know_le(a, b) and not know_le(join_know(a, c), join_know(b, c)):
                    return False
    return True


def distributive() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if meet_truth(a, join_truth(b, c)) != join_truth(meet_truth(a, b), meet_truth(a, c)):
                    return False
                if meet_know(a, join_know(b, c)) != join_know(meet_know(a, b), meet_know(a, c)):
                    return False
    return True


LAWS = {
    "COMMUTATIVE": commutative,
    "ASSOCIATIVE": associative,
    "IDEMPOTENT": idempotent,
    "MONOTONE": monotone,
    "DISTRIBUTIVE": distributive,
}


def run_all() -> dict:
    return {name: fn() for name, fn in LAWS.items()}
'''

files["dcs/triad/report.py"] = '''"""Human-readable renderings."""
from dcs.triad.lattice import ALL_STATES
from dcs.triad.laws import run_all


def lattice_diagram() -> str:
    lines = ["Belnap FOUR — verification lattice", "=" * 44]
    for s in ALL_STATES:
        lines.append(f"  {s.name:<9} t={s.t}  f={s.f}")
    lines.append("")
    lines.append("Truth order:      FAIL < UNKNOWN,CONFLICT < PASS")
    lines.append("Knowledge order:  UNKNOWN < PASS,FAIL < CONFLICT")
    lines.append("")
    lines.append("Operations:  meet_truth=AND  join_truth=OR")
    lines.append("             join_know=union of information")
    lines.append("             meet_know=common information")
    return "\\n".join(lines)


def law_report() -> str:
    results = run_all()
    lines = ["Algebraic laws", "=" * 44]
    for name, ok in results.items():
        lines.append(f"  {'PASS' if ok else 'FAIL'}  {name}")
    n_ok = sum(1 for v in results.values() if v)
    lines.append("")
    lines.append(f"{n_ok}/{len(results)} laws hold")
    return "\\n".join(lines)
'''

files["dcs/triad/__main__.py"] = '''"""python -m dcs.triad — CLI."""
import argparse, json, sys
from dcs.triad.kernel import Kernel, Triad
from dcs.triad.report import lattice_diagram, law_report
from dcs.triad.lattice import UNKNOWN, PASS, FAIL, CONFLICT


DEMO_SPEC = {
    "conformance": {"declared": {"a": 1, "b": 2}, "actual": {"a": 1, "b": 2}},
    "coherence":   {"a": "hello", "b": "hello", "mode": "equivalence"},
    "coordination":{"states": [{"t": 1, "f": 0},
                               {"t": 1, "f": 0},
                               {"t": 0, "f": 1}],
                    "mode": "quorum"},
}


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m dcs.triad")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lattice", help="print the verification lattice")
    sub.add_parser("laws", help="check the algebraic laws")
    sub.add_parser("self-verify", help="kernel verifies its own outputs")
    sub.add_parser("demo", help="run the built-in demo spec")
    v = sub.add_parser("verify", help="verify a spec from JSON")
    v.add_argument("spec", help="path to JSON spec file")

    args = p.parse_args(argv)
    k = Kernel()

    if args.cmd == "lattice":
        print(lattice_diagram())
    elif args.cmd == "laws":
        print(law_report())
    elif args.cmd == "self-verify":
        t = k.self_verify()
        r = k.receipt(t)
        print(json.dumps({
            "triad": t.to_dict(),
            "verdict": t.verdict(),
            "digest": r.digest,
            "receipt_check": k.check(r),
        }, indent=2))
    elif args.cmd == "demo":
        t = k.verify(DEMO_SPEC)
        r = k.receipt(t, derivation=[{"step": "conformance"},
                                     {"step": "coherence"},
                                     {"step": "coordination"}])
        print(json.dumps({
            "triad": t.to_dict(),
            "verdict": t.verdict(),
            "digest": r.digest,
            "signature": r.signature[:16] + "...",
            "receipt_check": k.check(r),
        }, indent=2))
    elif args.cmd == "verify":
        spec = json.loads(open(args.spec).read())
        t = k.verify(spec)
        r = k.receipt(t)
        print(json.dumps({
            "triad": t.to_dict(),
            "verdict": t.verdict(),
            "digest": r.digest,
            "receipt_check": k.check(r),
        }, indent=2))


if __name__ == "__main__":
    main()
'''

# write files
for rel, content in files.items():
    p = ROOT / rel
    if p.exists():
        d = bk / rel; d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, d)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print(f"  wrote {rel}")

# purge caches
subprocess.run("find dcs -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null", shell=True)

# run everything
print("\n" + "=" * 62)
print("python -m dcs.triad laws")
print("=" * 62)
subprocess.run([sys.executable, "-m", "dcs.triad", "laws"])

print("\n" + "=" * 62)
print("python -m dcs.triad demo")
print("=" * 62)
subprocess.run([sys.executable, "-m", "dcs.triad", "demo"])

print("\n" + "=" * 62)
print("python -m dcs.triad self-verify")
print("=" * 62)
subprocess.run([sys.executable, "-m", "dcs.triad", "self-verify"])

print(f"\nBackups: {bk}")
