"""Full coverage for dcs.triad.*"""
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from dcs.triad import laws, report
from dcs.triad.__main__ import DEMO_SPEC
from dcs.triad.__main__ import main as triad_main
from dcs.triad.axes import coherence, conformance, coordination
from dcs.triad.kernel import (
    KERNEL_VERSION,
    Kernel,
    Receipt,
    Triad,
    _canon,
    _digest,
    _sign,
)
from dcs.triad.lattice import (
    CONFLICT,
    FAIL,
    PASS,
    UNKNOWN,
    VState,
    consensus,
    fold_v,
    join_know,
    join_truth,
    know_le,
    meet_know,
    meet_truth,
    quorum,
    truth_le,
)


def test_vstate_names():
    assert VState(0,0).name == "UNKNOWN"
    assert VState(1,0).name == "PASS"
    assert VState(0,1).name == "FAIL"
    assert VState(1,1).name == "CONFLICT"


def test_vstate_repr():
    assert repr(PASS) == "PASS"


def test_vstate_to_dict():
    assert PASS.to_dict() == {"t": 1, "f": 0, "name": "PASS"}


def test_vstate_invalid():
    with pytest.raises(ValueError):
        VState(2, 0)


def test_vstate_from_any():
    assert VState.from_any(PASS) is PASS
    assert VState.from_any({"t": 1, "f": 0}) == PASS
    assert VState.from_any("pass") == PASS
    with pytest.raises(TypeError):
        VState.from_any(123)


def test_orders():
    assert truth_le(FAIL, UNKNOWN)
    assert not truth_le(PASS, UNKNOWN)
    assert know_le(UNKNOWN, PASS)
    assert not know_le(PASS, UNKNOWN)


def test_ops():
    assert meet_truth(PASS, UNKNOWN) == UNKNOWN
    assert join_truth(FAIL, UNKNOWN) == UNKNOWN
    assert meet_know(PASS, FAIL) == UNKNOWN
    assert join_know(PASS, FAIL) == CONFLICT


def test_fold_v_empty():
    assert fold_v([], meet_truth) == UNKNOWN


def test_fold_v_empty_with_default():
    assert fold_v([], meet_truth, empty=CONFLICT) == CONFLICT


def test_fold_v_single():
    assert fold_v([PASS], meet_truth) == PASS


def test_fold_v_two():
    assert fold_v([PASS, FAIL], meet_truth) == FAIL
    assert fold_v([PASS, PASS], meet_truth) == PASS


def test_consensus():
    assert consensus([]) == UNKNOWN
    assert consensus([PASS, PASS]) == PASS
    assert consensus([PASS, FAIL]) == CONFLICT


def test_quorum():
    assert quorum([]) == UNKNOWN
    assert quorum([PASS, PASS, FAIL]) == PASS
    assert quorum([FAIL, FAIL, PASS]) == FAIL
    assert quorum([PASS, FAIL]) == CONFLICT
    assert quorum([UNKNOWN, UNKNOWN, UNKNOWN]) == CONFLICT


def test_coherence_equivalence():
    assert coherence.equivalence(1, 1, eq=lambda a, b: a == b) == PASS
    assert coherence.equivalence(1, 2, eq=lambda a, b: a == b) == FAIL


def test_coherence_equivalence_raises():
    assert coherence.equivalence(1, 2, eq=lambda a, b: 1/0) == UNKNOWN


def test_coherence_refinement():
    assert coherence.refinement(1, 2, implies=lambda a, b: a <= b) == PASS
    assert coherence.refinement(2, 1, implies=lambda a, b: a <= b) == FAIL


def test_coherence_refinement_raises():
    assert coherence.refinement(1, 2, implies=lambda a, b: 1/0) == UNKNOWN


def test_coherence_incompatible():
    assert coherence.incompatible(1, 2, disjoint=lambda a, b: a != b) == PASS
    assert coherence.incompatible(1, 1, disjoint=lambda a, b: a != b) == FAIL


def test_coherence_incompatible_raises():
    assert coherence.incompatible(1, 2, disjoint=lambda a, b: 1/0) == UNKNOWN


def test_coherence_relation():
    assert coherence.relation(1, 2, rel=lambda a, b: True) == PASS
    assert coherence.relation(1, 2, rel=lambda a, b: False) == FAIL
    assert coherence.relation(1, 2, rel=lambda a, b: None) == UNKNOWN
    assert coherence.relation(1, 2, rel=lambda a, b: 1/0) == UNKNOWN


def test_coherence_combine():
    assert coherence.combine([PASS, FAIL]) == CONFLICT
    assert coherence.combine([PASS, PASS]) == PASS


def test_conformance_resolve_default():
    assert conformance.resolve(1, 1) == PASS
    assert conformance.resolve(1, 2) == FAIL


def test_conformance_resolve_compare():
    assert conformance.resolve(1, 2, compare=lambda a, b: True) == PASS
    assert conformance.resolve(1, 2, compare=lambda a, b: False) == FAIL


def test_conformance_resolve_raises():
    assert conformance.resolve(1, 2, compare=lambda a, b: 1/0) == UNKNOWN


def test_conformance_schema():
    assert conformance.schema({"a"}, {"a", "b"}) == PASS
    assert conformance.schema({"a"}, {"b"}) == FAIL
    assert conformance.schema(set(), set()) == UNKNOWN


def test_conformance_behavioral():
    assert conformance.behavioral(lambda x: x > 0, [1, 2, 3]) == PASS
    assert conformance.behavioral(lambda x: x > 0, [-1, -2, -3]) == FAIL
    assert conformance.behavioral(lambda x: x > 0, [1, -1, 2, -2]) == FAIL
    assert conformance.behavioral(lambda x: x > 0, [1, 2, -1]) == UNKNOWN
    assert conformance.behavioral(lambda x: x > 0, []) == UNKNOWN


def test_conformance_certificate():
    assert conformance.certificate({}, {}, verifier=lambda c, x: True) == PASS
    assert conformance.certificate({}, {}, verifier=lambda c, x: False) == FAIL
    assert conformance.certificate({}, {}, verifier=lambda c, x: 1/0) == UNKNOWN


def test_coordination_merge():
    assert coordination.merge([PASS, FAIL]) == CONFLICT


def test_coordination_conjunction():
    assert coordination.conjunction([PASS, FAIL]) == FAIL


def test_coordination_disjunction():
    assert coordination.disjunction([PASS, FAIL]) == PASS


def test_coordination_consensus():
    assert coordination.consensus([PASS, PASS]) == PASS


def test_coordination_quorum():
    assert coordination.quorum([PASS, PASS, FAIL]) == PASS


def test_coordination_veto():
    assert coordination.veto([]) == UNKNOWN
    assert coordination.veto([PASS, CONFLICT]) == CONFLICT
    assert coordination.veto([PASS, FAIL]) == FAIL
    assert coordination.veto([PASS, PASS]) == PASS
    assert coordination.veto([PASS, UNKNOWN]) == UNKNOWN


def test_coordination_weighted():
    assert coordination.weighted([PASS, FAIL], weights=[1, 1]) == CONFLICT
    assert coordination.weighted([PASS, FAIL], weights=[2, 1]) == PASS
    assert coordination.weighted([PASS, FAIL], weights=[1, 2]) == FAIL
    assert coordination.weighted([]) == UNKNOWN
    assert coordination.weighted([PASS], weights=[0]) == UNKNOWN
    assert coordination.weighted([UNKNOWN, UNKNOWN], weights=[1, 1]) == UNKNOWN
    with pytest.raises(ValueError):
        coordination.weighted([PASS], weights=[1, 2])


def test_triad_to_dict():
    t = Triad(PASS, FAIL, UNKNOWN)
    assert t.to_dict() == {
        "conformance": PASS.to_dict(),
        "coherence": FAIL.to_dict(),
        "coordination": UNKNOWN.to_dict()}


def test_triad_verdict_fail():
    assert Triad(PASS, FAIL, PASS).verdict() == "FAIL"


def test_triad_verdict_pass():
    assert Triad(PASS, PASS, PASS).verdict() == "PASS"


def test_triad_verdict_unknown():
    assert Triad(PASS, PASS, UNKNOWN).verdict() == "UNKNOWN"


def test_triad_verdict_conflict():
    assert Triad(PASS, CONFLICT, PASS).verdict() == "CONFLICT"


def test_triad_conjunction():
    a = Triad(PASS, PASS, PASS); b = Triad(FAIL, PASS, PASS)
    assert a.conjunction(b).conformance == meet_truth(PASS, FAIL)


def test_triad_disjunction():
    a = Triad(PASS, PASS, PASS); b = Triad(FAIL, FAIL, FAIL)
    assert a.disjunction(b).conformance == join_truth(PASS, FAIL)


def test_triad_merge():
    a = Triad(PASS, PASS, PASS); b = Triad(FAIL, FAIL, FAIL)
    assert a.merge(b).conformance == join_know(PASS, FAIL)


def test_receipt_to_dict():
    t = Triad(PASS, PASS, PASS); r = Receipt(t, (), "d", "s", "v")
    assert r.to_dict() == {"triad": t.to_dict(), "derivation": [],
                            "digest": "d", "signature": "s", "kernel_version": "v"}


def test_canon():
    assert _canon({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_digest():
    assert _digest({"a": 1}) == hashlib.sha256(b'{"a":1}').hexdigest()


def test_sign():
    assert _sign("d", "v") == hashlib.sha256(b"v:d").hexdigest()


def test_kernel_init():
    assert Kernel().version == KERNEL_VERSION


def test_kernel_conformance():
    assert Kernel().conformance(1, 1) == PASS


def test_kernel_coherence_equivalence():
    assert Kernel().coherence(1, 1) == PASS


def test_kernel_coherence_refinement():
    assert Kernel().coherence(1, 1, mode="refinement") == PASS


def test_kernel_coherence_incompatibility():
    # default relation is x==y, so disjoint(1,1)=True -> PASS
    assert Kernel().coherence(1, 1, mode="incompatibility") == PASS
    assert Kernel().coherence(1, 2, mode="incompatibility") == FAIL


def test_kernel_coherence_relation():
    assert Kernel().coherence(1, 1, mode="relation", relation=lambda a, b: True) == PASS


def test_kernel_coherence_unknown_mode():
    with pytest.raises(ValueError):
        Kernel().coherence(1, 1, mode="bad")


def test_kernel_coordination_all_modes():
    k = Kernel()
    for mode in ["merge", "conjunction", "disjunction", "consensus", "quorum", "veto"]:
        assert k.coordination([PASS, PASS], mode=mode) == PASS


def test_kernel_coordination_unknown_mode():
    with pytest.raises(ValueError):
        Kernel().coordination([], mode="bad")


def test_kernel_verify_empty():
    assert Kernel().verify({}) == Triad(UNKNOWN, UNKNOWN, UNKNOWN)


def test_kernel_verify_conformance_only():
    assert Kernel().verify({"conformance": {"declared": 1, "actual": 1}}).conformance == PASS


def test_kernel_verify_coherence_only():
    assert Kernel().verify({"coherence": {"a": 1, "b": 1}}).coherence == PASS


def test_kernel_verify_coordination_only():
    assert Kernel().verify({"coordination": {"states": [{"t": 1, "f": 0}]}}).coordination == PASS


def test_kernel_receipt_and_check():
    k = Kernel(); r = k.receipt(Triad(PASS, PASS, PASS), derivation=[{"step": "test"}])
    assert k.check(r) is True


def test_kernel_check_wrong_version():
    k = Kernel(); r = k.receipt(Triad(PASS, PASS, PASS))
    assert Kernel(version="other").check(r) is False


def test_kernel_check_wrong_digest():
    k = Kernel(); t = Triad(PASS, PASS, PASS); r = k.receipt(t)
    assert k.check(Receipt(t, r.derivation, "wrong", r.signature, r.kernel_version)) is False


def test_kernel_check_wrong_signature():
    k = Kernel(); t = Triad(PASS, PASS, PASS); r = k.receipt(t)
    assert k.check(Receipt(t, r.derivation, r.digest, "wrong", r.kernel_version)) is False


def test_kernel_self_verify():
    assert isinstance(Kernel().self_verify(), Triad)


def test_laws_all_pass():
    assert laws.commutative() and laws.associative() and laws.idempotent()
    assert laws.monotone() and laws.distributive()


def test_laws_run_all():
    res = laws.run_all()
    assert all(res.values())
    assert set(res.keys()) == set(laws.LAWS.keys())


def test_lattice_diagram():
    assert "Belnap FOUR" in report.lattice_diagram()


def test_law_report():
    s = report.law_report()
    assert "Algebraic laws" in s and "5/5" in s


def test_main_lattice(capsys):
    triad_main(["lattice"]); assert "Belnap FOUR" in capsys.readouterr().out


def test_main_laws(capsys):
    triad_main(["laws"]); assert "Algebraic laws" in capsys.readouterr().out


def test_main_self_verify(capsys):
    triad_main(["self-verify"]); assert "triad" in capsys.readouterr().out


def test_main_demo(capsys):
    triad_main(["demo"]); assert "triad" in capsys.readouterr().out


def test_main_verify(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(DEMO_SPEC, f); spec = f.name
    try:
        triad_main(["verify", spec])
        assert "triad" in capsys.readouterr().out
    finally:
        Path(spec).unlink()
