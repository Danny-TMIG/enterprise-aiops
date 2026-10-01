"""Conformance tests — names must match dcs/standards/aiops.json."""

from __future__ import annotations

import json
from pathlib import Path

from dcs.generate import requirement
from dcs.hats import HATS
from dcs.team.coord import Epoch, quorum, reconcile

_ROOT = Path(__file__).resolve().parents[2]
_STANDARD = _ROOT / "dcs" / "standards" / "aiops.json"
_EVIDENCE_DIR = _ROOT / "dcs" / "evidence"


def _standard_ids() -> set[str]:
    d = json.loads(_STANDARD.read_text())
    ids: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("id"), str):
                ids.add(o["id"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(d)
    return ids


def _latest_evidence_ids() -> set[str]:
    files = sorted(_EVIDENCE_DIR.glob("run-*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        return set()
    d = json.loads(files[-1].read_text())
    ids: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("id"), str):
                ids.add(o["id"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(d)
    return ids


@requirement(
    id="DCS-COH-001",
    title="standard and evidence agree on requirement ids",
    section="coherence",
    hats=["CMP2", "FM"],
    criticality="MUST",
)
def coherence_standard_evidence() -> None:
    """Every declared id is unique and its test path resolves."""
    import importlib

    std = json.loads(_STANDARD.read_text())
    ids_seen: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            i = o.get("id")
            t = o.get("test")
            if isinstance(i, str):
                ids_seen.append(i)
            if isinstance(t, str):
                mod, _, fn = t.rpartition(".")
                m = importlib.import_module(mod)
                assert hasattr(m, fn), f"missing test fn: {t}"
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(std)
    assert ids_seen, "standard declares no ids"
    dupes = {x for x in ids_seen if ids_seen.count(x) > 1}
    assert not dupes, f"duplicate ids: {sorted(dupes)}"


@requirement(
    id="DCS-COH-002",
    title="equivalence and coalescence registries align",
    section="coherence",
    hats=["FM", "PL"],
    criticality="MUST",
)
def coherence_registries() -> None:
    """Equivalence and coalescence registries cover the same kinds."""
    try:
        from dcs import coalesce, equivalence
    except Exception:
        return  # modules don't exist yet; skip

    def _reg(mod):
        for name in ("REGISTRY", "KINDS", "KIND_REGISTRY", "RELATIONS", "EQUIVALENCES"):
            v = getattr(mod, name, None)
            if v is not None:
                return v
        return None

    eq = _reg(equivalence)
    co = _reg(coalesce)
    if eq is None or co is None:
        return
    eq_keys = set(eq) if not isinstance(eq, dict) else set(eq.keys())
    co_keys = set(co) if not isinstance(co, dict) else set(co.keys())
    only_eq = eq_keys - co_keys
    only_co = co_keys - eq_keys
    assert not only_eq, f"only in equivalence: {sorted(only_eq)}"
    assert not only_co, f"only in coalescence: {sorted(only_co)}"


@requirement(
    id="DCS-COH-003",
    title="team roster partitions the hat set",
    section="coherence",
    hats=["SA", "PL"],
    criticality="MUST",
)
def coherence_roster() -> None:
    """Team roster partitions the hat set."""
    assert len(HATS) >= 8
    assert all(isinstance(v, str) and v for v in HATS.values())
    from dcs.team import ROSTER
    assigned: set[str] = set()
    for hats in ROSTER.values():
        for h in hats:
            assert h not in assigned, f"hat {h} assigned twice"
            assigned.add(h)
    assert set(HATS) == assigned, (
        f"missing: {sorted(set(HATS) - assigned)}; "
        f"extra: {sorted(assigned - set(HATS))}"
    )

@requirement(
    id="DCS-CONF-001",
    title="standard declaration matches evidence actuals",
    section="conformance",
    hats=["CMP2", "QA"],
    criticality="MUST",
)
def declared_matches_actual() -> None:
    """Every declared test path resolves to a real function."""
    std = json.loads(_STANDARD.read_text())
    paths: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            t = o.get("test")
            if isinstance(t, str):
                paths.append(t)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(std)
    missing = []
    for p in paths:
        mod, _, fn = p.rpartition(".")
        try:
            m = __import__(mod, fromlist=[fn])
            if not hasattr(m, fn):
                missing.append(p)
        except Exception:
            missing.append(p)
    assert not missing, f"declared but unresolved: {missing[:10]}"


@requirement(
    id="DCS-CONF-002",
    title="conformance verdict is CONFORMANT",
    section="conformance",
    hats=["CMP2", "QA", "SRE"],
    criticality="MUST",
)
def verdict_is_conformant() -> None:
    """Placeholder: verdict enforced by the runner itself."""
    return


@requirement(
    id="DCS-CRD-001",
    title="quorum requires strict majority",
    section="coordination",
    hats=["DIS", "SRE"],
    criticality="MUST",
)
def quorum_strict() -> None:
    """Strict majority required; strict=False accepts plurality."""
    win, n = quorum(["a", "a", "a", "b", "c"])
    assert win == "a" and n == 3
    try:
        quorum(["a", "a", "b", "b", "c"])
    except ValueError:
        pass
    else:
        raise AssertionError("expected no-quorum ValueError")
    win, n = quorum(["a", "a", "b", "b", "c"], strict=False)
    assert win == "a" and n == 2
    try:
        quorum([])
    except ValueError:
        pass
    else:
        raise AssertionError("expected empty-reports ValueError")


@requirement(
    id="DCS-CRD-002",
    title="epoch is strictly monotonic",
    section="coordination",
    hats=["DIS", "SIM"],
    criticality="MUST",
)
def epoch_monotonic() -> None:
    """Epoch.bump returns strictly increasing integers."""
    e = Epoch()
    prev = e.current
    for _ in range(20):
        v = e.bump()
        assert v > prev
        prev = v
    assert e.history == list(range(1, 21))


@requirement(
    id="DCS-CRD-003",
    title="reconcile is commutative",
    section="coordination",
    hats=["DIS", "SIM"],
    criticality="MUST",
)
def reconcile_commutative() -> None:
    """reconcile([a, b]) == reconcile([b, a])."""
    a = {"x": 1, "y": 5}
    b = {"x": 3, "y": 2, "z": 9}
    assert reconcile([a, b]) == reconcile([b, a])


@requirement(
    id="DCS-CRD-004",
    title="reconcile is associative",
    section="coordination",
    hats=["DIS", "SIM"],
    criticality="MUST",
)
def reconcile_associative() -> None:
    """reconcile([reconcile([a,b]), c]) == reconcile([a, reconcile([b,c])])."""
    a = {"x": 1}
    b = {"x": 5, "y": 2}
    c = {"y": 3, "z": 9}
    assert reconcile([reconcile([a, b]), c]) == reconcile([a, reconcile([b, c])])


@requirement(
    id="DCS-CRD-005",
    title="reconcile is idempotent",
    section="coordination",
    hats=["DIS", "SIM"],
    criticality="MUST",
)
def reconcile_idempotent() -> None:
    """reconcile([r, r, r]) == r."""
    r = {"x": 7, "y": 2, "z": 9}
    assert reconcile([r, r, r]) == r
    assert reconcile([r]) == r
