"""Smoke tests. Each imported module is exercised at least once."""
from dcs import bisim, coherence, verify, verify_intoto


def test_verify_public_surface():
    v = verify.HMACVerifier(b"k")
    sig = v.sign(b"m").hex()
    assert verify.verify(b"m", sig, v).ok


def test_verify_intoto_public_surface():
    v = verify.HMACVerifier(b"k")
    stmt = verify_intoto.Statement(
        subject=[verify_intoto.Subject.of("f", b"x")],
        predicate_type="t",
        predicate={},
    )
    env = verify_intoto.sign_statement(stmt, v)
    assert verify_intoto.verify_envelope(env, v)


def test_coherence_public_surface():
    assert coherence.coherent({"a": 1}, {"a": 1})
    assert coherence.incoherent_keys({"a": 1}, {"a": 2}) == ["a"]


def test_bisim_public_surface():
    lts = {"a": [("x", "b")], "b": []}
    assert bisim.bisimilar(lts, "a", "a")
    assert isinstance(bisim.equivalence_classes(lts), dict)


def test_verify_module_helpers():
    assert verify.digest_of(b"x") == verify.digest_of("x")
    assert verify.canonical({"b": 1, "a": 2}) == b'{"a":2,"b":1}'
