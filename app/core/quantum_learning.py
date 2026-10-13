"""Quantum Learning (codeQL) — two-space execution fabric.

CLOSURE  (C):  sigma |= T_c   — self-referential; the scaffolding.
EVOLUTION(E):  sigma' |= eps  — held-out; the mutation gate.

A mutation that only satisfies C is circular. A mutation that
satisfies C and E is demonstrated learning. The loop commits nothing
else.

Self-registers as capability `quantum_learning`.
"""
from __future__ import annotations

import hashlib
import os
import random
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
PY = sys.executable
ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


# ── data types ──────────────────────────────────────────────────────
@dataclass(frozen=True)
class Failure:
    file: str
    line: int
    exc: str
    msg: str

    def key(self) -> str:
        return f"{Path(self.file).name}:{self.line}:{self.exc}"


@dataclass(frozen=True)
class Sample:
    """Held-out entropy sample epsilon. Never shown to a fixer."""
    id: str
    kind: str          # "test" | "assert"
    payload: str
    seed: int = 0

    @staticmethod
    def from_test_id(tid: str, seed: int = 0) -> Sample:
        h = hashlib.sha1(tid.encode()).hexdigest()[:10]
        return Sample(id=h, kind="test", payload=tid, seed=seed)


@dataclass
class Verdict:
    ok: bool
    detail: str = ""
    output: str = ""


@dataclass
class Mutation:
    state_before: str
    state_after: str
    failure: Failure
    sample: Sample
    c_valid: bool
    e_valid: bool
    diff: str = ""
    committed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    iterations: int
    committed: int
    refused: int
    final_status: str
    mutations: list[Mutation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mutations"] = [m.to_dict() for m in self.mutations]
        return d


# ── closure space ───────────────────────────────────────────────────
class ClosureSpace:
    """C: sigma |= T_c. Runs the visible suite."""

    def __init__(self, tests: Sequence[str], root: Path = ROOT):
        self.tests = list(tests)
        self.root = root

    def validate(self) -> Verdict:
        cmd = [PY, "-m", "pytest", "-q", "--no-header",
               "-p", "no:cacheprovider", "--tb=line", *self.tests]
        r = subprocess.run(cmd, cwd=self.root, env=ENV,
                           capture_output=True, text=True)
        return Verdict(ok=(r.returncode == 0),
                       detail=f"pytest exit={r.returncode}",
                       output=r.stdout + r.stderr)

    def validate_after(self, patch: Callable[[], None]) -> Verdict:
        snap = _snapshot(self.root, self.tests)
        try:
            patch()
            return self.validate()
        finally:
            if not _changed_ok(self.root, snap):
                _restore(snap)


# ── evolution space ─────────────────────────────────────────────────
class EvolutionSpace:
    """E: sigma' |= eps. Samples drawn before mutation, held out."""

    def __init__(self, samples: Sequence[Sample],
                 rng: random.Random | None = None):
        self._pool = list(samples)
        self._rng = rng or random.Random(0)
        self._used: set = set()

    def sample(self) -> Sample | None:
        fresh = [s for s in self._pool if s.id not in self._used]
        if not fresh:
            return None
        s = self._rng.choice(fresh)
        self._used.add(s.id)
        return s

    def validate(self, s: Sample, root: Path = ROOT) -> Verdict:
        if s.kind == "test":
            cmd = [PY, "-m", "pytest", "-q", "--no-header",
                   "-p", "no:cacheprovider", "--tb=short", s.payload]
            r = subprocess.run(cmd, cwd=root, env=ENV,
                               capture_output=True, text=True)
            return Verdict(ok=(r.returncode == 0),
                           detail=f"eps={s.id} {s.payload}",
                           output=r.stdout + r.stderr)
        if s.kind == "assert":
            r = subprocess.run([PY, "-c", s.payload], cwd=root, env=ENV,
                               capture_output=True, text=True)
            return Verdict(ok=(r.returncode == 0), detail=f"eps={s.id}",
                           output=r.stdout + r.stderr)
        return Verdict(ok=False, detail=f"unknown sample kind {s.kind}")


# ── snapshot helpers ────────────────────────────────────────────────
@dataclass
class Snapshot:
    tests: Sequence[str]
    files: dict[Path, bytes] = field(default_factory=dict)

    def restore(self) -> None:
        _restore(self.files)


def _snapshot(root: Path, tests: Sequence[str]) -> dict[Path, bytes]:
    out: dict[Path, bytes] = {}
    seen: set = set()
    for t in tests:
        p = (root / t).resolve()
        if p.is_dir():
            iterable = p.rglob("*.py")
        elif p.exists():
            iterable = [p]
        else:
            iterable = []
        for f in iterable:
            if f in seen or not f.exists():
                continue
            seen.add(f)
            out[f] = f.read_bytes()
    for sub in ("app", "scripts"):
        d = root / sub
        if d.exists():
            for f in d.rglob("*.py"):
                if f not in seen and f.exists():
                    seen.add(f)
                    out[f] = f.read_bytes()
    return out


def _restore(snap: dict[Path, bytes]) -> None:
    for f, data in snap.items():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)


def _changed_ok(root: Path, snap: dict[Path, bytes]) -> bool:
    for f, data in snap.items():
        if not f.exists() or f.read_bytes() != data:
            return False
    return True


def _hash_tree(root: Path, tests: Sequence[str]) -> str:
    h = hashlib.sha1()
    for f in sorted(_snapshot(root, tests)):
        h.update(str(f).encode())
        h.update(b"\x00")
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _diff(snap: dict[Path, bytes]) -> str:
    out = []
    for f, old in snap.items():
        if f.exists() and f.read_bytes() != old:
            out.append(f"--- {f}\n+++ patched ({len(old)} -> "
                       f"{len(f.read_bytes())} bytes)")
    return "\n".join(out)


LINE_RE = re.compile(
    r"^(?P<file>[^:\n]+\.py):(?P<line>\d+): (?P<exc>\w+): (?P<msg>.*)$")


def _first_failure(output: str) -> Failure | None:
    for ln in output.splitlines():
        m = LINE_RE.match(ln.strip())
        if m:
            return Failure(m["file"], int(m["line"]),
                           m["exc"], m["msg"])
    return None


# ── mutation operator ───────────────────────────────────────────────
Fixer = Callable[[Failure, Snapshot], Callable[[], None] | None]


def mutate(state: Any, failure: Failure, sample: Sample,
           fixers: Sequence[Fixer],
           closure: ClosureSpace,
           evolution: EvolutionSpace) -> Mutation:
    """mu(sigma, f, eps) -> sigma'. Commits only if C and E both hold."""
    before = _hash_tree(ROOT, closure.tests)
    mut = Mutation(state_before=before, state_after=before,
                   failure=failure, sample=sample,
                   c_valid=False, e_valid=False)

    for fx in fixers:
        try:
            patch = fx(failure, Snapshot(closure.tests))
        except Exception:
            continue
        if patch is None:
            continue

        snap = _snapshot(ROOT, closure.tests)
        try:
            patch()
            c = closure.validate()
            mut.c_valid = c.ok
            mut.diff = _diff(snap)
            if not c.ok:
                _restore(snap)
                continue
            e = evolution.validate(sample)
            mut.e_valid = e.ok
            if not e.ok:
                _restore(snap)
                mut.diff += "\n[E-refused]\n" + e.output[-400:]
                continue
            mut.state_after = _hash_tree(ROOT, closure.tests)
            mut.committed = True
            return mut
        except Exception:
            _restore(snap)
            continue
    return mut


# ── loop ────────────────────────────────────────────────────────────
class QuantumLoop:
    def __init__(self, closure: ClosureSpace, evolution: EvolutionSpace,
                 fixers: Sequence[Fixer]):
        self.closure = closure
        self.evolution = evolution
        self.fixers = fixers

    def run(self, max_iter: int = 16) -> Report:
        rep = Report(iterations=0, committed=0, refused=0,
                     final_status="running")
        for i in range(1, max_iter + 1):
            rep.iterations = i
            c = self.closure.validate()
            if c.ok:
                rep.final_status = "C-valid (no open failures)"
                return rep
            failure = _first_failure(c.output)
            if failure is None:
                rep.final_status = "no parseable failure"
                return rep
            eps = self.evolution.sample()
            if eps is None:
                rep.final_status = "entropy pool exhausted"
                return rep
            m = mutate(None, failure, eps, self.fixers,
                       self.closure, self.evolution)
            rep.mutations.append(m)
            if m.committed:
                rep.committed += 1
                continue
            rep.refused += 1
            if rep.refused >= 3:
                rep.final_status = "refused: no mutation generalizes"
                return rep
        rep.final_status = "max iterations"
        return rep


__all__ = [
    "ClosureSpace",
    "EvolutionSpace",
    "Failure",
    "Mutation",
    "QuantumLoop",
    "Report",
    "Sample",
    "Snapshot",
    "Verdict",
    "mutate",
]


# ── self-registration ──────────────────────────────────────────────
def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("quantum_learning")
    def _entrypoint(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "module": "app.core.quantum_learning",
            "classes": ["ClosureSpace", "EvolutionSpace", "QuantumLoop"],
            "operator": "mutate",
        }


_self_register()


# ── self-registration as capability `quantum_loop` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("quantum_loop")
    def _entry(*args, **kwargs):
        return {"module": "app.core.quantum_learning", "code": "quantum_loop"}


_self_register()
