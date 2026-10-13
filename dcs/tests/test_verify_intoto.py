"""Unit tests for dcs.verify_intoto."""
from dcs.verify import HMACVerifier
from dcs.verify_intoto import (
    PAYLOAD_TYPE,
    STATEMENT_TYPE,
    Envelope,
    Statement,
    Subject,
    sign_statement,
    verify_envelope,
)


KEY = b"intoto-test-key"


def _statement():
    return Statement(
        subject=[Subject.of("build.py", b"print(1)")],
        predicate_type="https://example.com/build/v1",
        predicate={"command": "python build.py", "return_code": 0},
    )


def test_subject_of_computes_digest():
    s = Subject.of("f.txt", b"hello")
    assert s.name == "f.txt"
    assert "sha256" in s.digest
    assert len(s.digest["sha256"]) == 64


def test_statement_to_json_shape():
    j = _statement().to_json()
    assert j["_type"] == STATEMENT_TYPE
    assert j["predicateType"] == "https://example.com/build/v1"
    assert j["subject"][0]["name"] == "build.py"


def test_sign_verify_roundtrip():
    v = HMACVerifier(KEY)
    env = sign_statement(_statement(), v)
    assert verify_envelope(env, v)


def test_verify_fails_on_tampered_statement():
    v = HMACVerifier(KEY)
    env = sign_statement(_statement(), v)
    tampered = Envelope(statement={"x": 1}, signature=env.signature)
    assert not verify_envelope(tampered, v)


def test_verify_fails_on_tampered_signature():
    v = HMACVerifier(KEY)
    env = sign_statement(_statement(), v)
    tampered = Envelope(statement=env.statement, signature="00" * 32)
    assert not verify_envelope(tampered, v)


def test_verify_fails_on_malformed_signature():
    v = HMACVerifier(KEY)
    env = sign_statement(_statement(), v)
    tampered = Envelope(statement=env.statement, signature="not-hex")
    assert not verify_envelope(tampered, v)


def test_envelope_to_json_shape():
    v = HMACVerifier(KEY)
    env = sign_statement(_statement(), v)
    j = env.to_json()
    assert j["payloadType"] == PAYLOAD_TYPE
    assert "payload" in j
    assert j["signatures"][0]["sig"] == env.signature


def test_verify_fails_with_wrong_key():
    v1 = HMACVerifier(KEY)
    v2 = HMACVerifier(b"different-key")
    env = sign_statement(_statement(), v1)
    assert not verify_envelope(env, v2)
