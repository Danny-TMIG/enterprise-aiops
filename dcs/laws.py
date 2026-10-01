"""Law catalog: every invariant the system claims.

Each law is (name, statement, kind, predicate). The predicate is an
executable assertion. `dcs laws` runs them all. Failure names the law.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from dcs import coalesce, equivalence


@dataclass
class Law:
    name: str
    statement: str
    domain: str
    predicate: Callable[[], None]


LAWS: list[Law] = []


def law(name: str, statement: str, domain: str):
    def deco(fn):
        LAWS.append(Law(name=name, statement=statement, domain=domain, predicate=fn))
        return fn

    return deco


# ── Equivalence laws ─────────────────────────────────────────────
@law("EQ-REFLEXIVE", "∀k,a: semantic(k,a,a)", "equivalence")
def _():
    from app.train.core import TrainConfig, Trainer

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r = tr.step(0)
    assert equivalence.semantic("Run", r, r)


@law("EQ-SYMMETRIC", "∀k,a,b: semantic(k,a,b) ⇒ semantic(k,b,a)", "equivalence")
def _():
    from app.train.core import TrainConfig, Trainer

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    a, b = tr.step(0), tr.step(0)
    assert equivalence.semantic("Run", a, b) == equivalence.semantic("Run", b, a)


@law("EQ-EXACT-IMPLIES-SEMANTIC", "∀k,a,b: exact(k,a,b) ⇒ semantic(k,a,b)", "equivalence")
def _():
    from app.train import mesh as m
    from app.train.core import TrainConfig, Trainer

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r = tr.step(0)
    for kind, (a, b) in {
        "Run": (r, r),
        "Weave": (m.weave([r]), m.weave([r])),
        "MeshOfMeshes": (m.MeshOfMeshes([r]), m.MeshOfMeshes([r])),
    }.items():
        if equivalence.exact(kind, a, b):
            assert equivalence.semantic(kind, a, b), kind


# ── Coalescence laws ─────────────────────────────────────────────
@law("CO-COMMUTATIVE-MESH", "merge(Mesh)(a,b) ≡ merge(Mesh)(b,a)", "coalescence")
def _():
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import MeshOfMeshes

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r0, r1 = tr.step(0), tr.step(1)
    ab = coalesce.merge("MeshOfMeshes", MeshOfMeshes([r0]), MeshOfMeshes([r1])).value
    ba = coalesce.merge("MeshOfMeshes", MeshOfMeshes([r1]), MeshOfMeshes([r0])).value
    assert equivalence.semantic("MeshOfMeshes", ab, ba)


@law("CO-IDEMPOTENT-MESH", "merge(Mesh)(a,a) ≡ a", "coalescence")
def _():
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import MeshOfMeshes

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r = tr.step(0)
    merged = coalesce.merge("MeshOfMeshes", MeshOfMeshes([r]), MeshOfMeshes([r])).value
    assert len(merged) == 1


@law("CO-REFUSES-DISAGREEMENT", "merge(Run) refuses if rates differ", "coalescence")
def _():
    from app.train.core import TrainConfig, Trainer

    t1 = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    t2 = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["hard"], puzzles_per_tile=1, seed=0))
    try:
        coalesce.merge("Run", t1.step(0), t2.step(0))
    except ValueError:
        return
    raise AssertionError("disagreement was merged")


@law("CO-STRICTER-WINS", "merge(Requirement)(a,b).crit == max(crit_a, crit_b)", "coalescence")
def _():
    from dcs.standard import Requirement

    a = Requirement(id="X", title="t", section="s", hats=["BE"], criticality="MAY", test="f")
    b = Requirement(id="X", title="t", section="s", hats=["BE"], criticality="MUST", test="f")
    assert coalesce.merge("Requirement", a, b).value.criticality == "MUST"
    assert coalesce.merge("Requirement", b, a).value.criticality == "MUST"


# ── Transparency laws ────────────────────────────────────────────
@law("LOG-APPEND-ONLY", "transparency log is a Merkle chain", "transparency")
def _():
    from pathlib import Path

    from dcs import transparency

    log = Path("/tmp/dcs_law_log.jsonl")
    log.unlink(missing_ok=True)
    for i in range(5):
        transparency.append(log, f"bundle-{i}", "CONFORMANT")
    r = transparency.verify_chain(log)
    assert r["valid"] and r["entries"] == 5


@law("LOG-TAMPER-DETECTED", "modifying a log entry invalidates the chain", "transparency")
def _():
    import json
    from pathlib import Path

    from dcs import transparency

    log = Path("/tmp/dcs_law_log2.jsonl")
    log.unlink(missing_ok=True)
    for i in range(3):
        transparency.append(log, f"b{i}", "CONFORMANT")
    lines = log.read_text().splitlines()
    e = json.loads(lines[1])
    e["bundle"] = "tampered"
    lines[1] = json.dumps(e)
    log.write_text("\n".join(lines) + "\n")
    r = transparency.verify_chain(log)
    assert not r["valid"]


# ── Evidence laws ────────────────────────────────────────────────
@law("EVIDENCE-DIGEST-STABLE", "same bundle → same digest", "evidence")
def _():
    from dcs.evidence import Bundle, RequirementResult

    def mk():
        b = Bundle(
            standard_ref="x@1",
            reference={"name": "r"},
            started=0.0,
            completed=1.0,
            results=[RequirementResult(id="R", criticality="MUST", pass_=True, duration_ms=0.0)],
        )
        return b.seal().to_dict()

    a, b = mk(), mk()
    assert a["digest"] == b["digest"]


@law("EVIDENCE-FAIL-FLIPS-VERDICT", "any MUST fail ⇒ NON_CONFORMANT", "evidence")
def _():
    from dcs.evidence import Bundle, RequirementResult

    b = Bundle(
        standard_ref="x@1",
        reference={},
        started=0.0,
        completed=1.0,
        results=[RequirementResult(id="R", criticality="MUST", pass_=False, duration_ms=0.0)],
    )
    b.seal()
    assert b.verdict() == "NON_CONFORMANT"


# ── Train-pipeline laws ──────────────────────────────────────────
@law("RUN-CHAIN-ACYCLIC", "parent_id chain terminates at root", "train")
def _():
    from app.train.core import TrainConfig, Trainer

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    seen, cur = set(), tr.step(0)
    for _ in range(3):
        cur = tr.step(0)
    while cur is not None:
        assert cur.digest not in seen, "cycle detected"
        seen.add(cur.digest)
        pid = cur.parent_id
        cur = next((r for r in tr.runs if r.digest == pid), None) if pid else None


@law("POLLINATE-PARTITION", "every pollinate entry is added | removed | changed", "train")
def _():
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import pollinate

    tr = Trainer(
        TrainConfig(kinds=["sudoku"], difficulties=["easy", "medium"], puzzles_per_tile=1, seed=0)
    )
    a, b = tr.step(0), tr.step(1)
    for p in pollinate(a, b):
        assert p["change"] in {"added", "removed", "changed"}


# ── Puzzle laws ──────────────────────────────────────────────────
@law("RUBIK-REPLAY-FIXES", "solve_cube output replays to SOLVED", "puzzles")
def _():
    from app.puzzles.rubik import MOVES, SOLVED, apply_move, scramble, solve_cube

    for d in (2, 4, 6, 8):
        s = scramble(n_moves=d, seed=42)
        r = solve_cube(s)
        cur = s
        for m in r["solution"]:
            cur = apply_move(MOVES[m], cur)
        assert cur == SOLVED, d


@law("RUBIK-SCRAMBLE-ESCAPES", "scramble never returns SOLVED", "puzzles")
def _():
    from app.puzzles.rubik import SOLVED, scramble

    for d in (2, 4, 6, 8, 10, 11):
        assert scramble(n_moves=d, seed=42) != SOLVED


# ── Cross-cutting laws ───────────────────────────────────────────
@law("CIRCUIT-OPENS", "circuit breaker opens after N failures", "crosscut")
def _():
    from dcs.crosscut.circuit import CircuitBreaker

    cb = CircuitBreaker(threshold=2, cooldown=10.0)

    def boom():
        raise ValueError()

    for _ in range(2):
        try:
            cb.call(0.0, boom)
        except ValueError:
            pass
    try:
        cb.call(1.0, boom)
    except RuntimeError:
        return
    raise AssertionError("breaker stayed closed")


@law("RATELIMIT-BURST", "token bucket admits exactly burst then holds", "crosscut")
def _():
    from dcs.crosscut.ratelimit import TokenBucket

    b = TokenBucket(rate=10.0, burst=5)
    assert sum(b.allow(0.0) for _ in range(20)) == 5


@law("SAGA-COMPENSATES-REVERSE", "saga undo runs in reverse order", "crosscut")
def _():
    from dcs.crosscut.saga import Saga

    log = []
    s = (
        Saga()
        .add(lambda c: log.append("d1"), lambda c: log.append("u1"))
        .add(lambda c: log.append("d2"), lambda c: log.append("u2"))
        .add(lambda c: (_ for _ in ()).throw(RuntimeError()), lambda c: log.append("u3"))
    )
    assert s.run({}) is False
    assert log == ["d1", "d2", "u2", "u1"]


@law("CLOCK-MONOTONIC", "injectable clock never goes backward", "crosscut")
def _():
    from dcs.crosscut.clock import Clock

    c = Clock()
    stamps = []
    for _ in range(5):
        stamps.append(c.now())
        c.advance(1)
    assert all(b >= a for a, b in zip(stamps, stamps[1:]))


@law("PRIVACY-REDACTS", "PII patterns removed", "crosscut")
def _():
    from dcs.crosscut.privacy import redact

    cleaned, n = redact("x@y.com 555-121-9999")
    assert n == 2 and "@" not in cleaned


@law("SEMVER-CARET-UPPER", "^1.0.0 excludes 2.0.0", "crosscut")
def _():
    from dcs.crosscut.semver import satisfies

    assert satisfies("1.9.9", "^1.0.0") and not satisfies("2.0.0", "^1.0.0")


@law("FLAG-DETERMINISTIC", "flag rollout is a pure function", "crosscut")
def _():
    from dcs.crosscut.flag import enabled

    assert enabled("x", "u1", 50) == enabled("x", "u1", 50)


@law("CDC-MONOTONIC", "CDC version stamps increase monotonically", "crosscut")
def _():
    from dcs.crosscut.cdc import CDC

    c = CDC()
    vs = [c.emit("put", f"k{i}") for i in range(5)]
    assert vs == sorted(vs) and len(set(vs)) == 5


@law("A11Y-CONTRAST", "black on white ≥ 4.5:1", "crosscut")
def _():
    from dcs.crosscut.a11y import contrast

    assert contrast((0, 0, 0), (255, 255, 255)) >= 4.5


@law("I18N-FALLBACK", "unknown locale falls back to en", "crosscut")
def _():
    from dcs.crosscut.i18n import t

    assert t("zz", "greeting", name="A") == "Hello, A"


@law("CHAOS-FRACTION", "injection rate ≈ configured probability", "crosscut")
def _(*a, **kw):
    from dcs.crosscut.chaos import test as _t

    _t()


def _try(h):
    try:
        h.maybe_fail()
        return False
    except RuntimeError:
        return True


@law("BACKUP-INTEGRITY", "tampered snapshot rejected", "crosscut")
def _():
    from dcs.crosscut.backup import restore, snapshot

    s = snapshot(b"payload")
    s["bytes"] = b"x"
    try:
        restore(s)
    except AssertionError:
        return
    raise AssertionError("tampered snapshot restored")


@law("CONCURRENCY-DEDUP", "single-flight collapses concurrent calls", "crosscut")
def _():
    import threading
    import time

    from dcs.crosscut.concurrency import SingleFlight

    sf = SingleFlight()
    calls = {"n": 0}

    def slow():
        calls["n"] += 1
        time.sleep(0.01)
        return 1

    ts = [threading.Thread(target=lambda: sf.do("k", slow)) for _ in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert calls["n"] <= 3, calls["n"]


@law("OBS-CARDINALITY", "metrics drop new series at ceiling", "crosscut")
def _():
    from dcs.crosscut.observability import Metrics

    m = Metrics(max_series=3)
    for i in range(50):
        m.inc("x", i=i)
    assert m.value("_dropped") > 0


@law("TIME-MONOTONIC", "monotonic clock is non-decreasing", "crosscut")
def _():
    import time

    a = time.monotonic()
    time.sleep(0.001)
    b = time.monotonic()
    assert b >= a


def run_all() -> dict:
    passed, failed = [], []
    for L in LAWS:
        try:
            L.predicate()
            passed.append(L.name)
        except Exception as e:
            failed.append((L.name, f"{type(e).__name__}: {e}"))
    return {
        "passed": passed,
        "failed": failed,
        "n_passed": len(passed),
        "n_failed": len(failed),
        "n_laws": len(LAWS),
    }
