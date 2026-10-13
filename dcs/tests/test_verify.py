"""Unit tests for dcs.verify."""
import pytest

from dcs.verify import (
    HMACVerifier,
    VerificationResult,
    canonical,
    digest_of,
    verify,
)


KEY = b"test-key-do-not-use-in-production"


def test_digest_is_deterministic():
    assert digest_of(b"abc") == digest_of(b"abc")
    assert digest_of(b"abc") == digest_of("abc")


def test_digest_differs_for_different_input():
    assert digest_of(b"abc") != digest_of(b"abd")


def test_canonical_sorts_keys():
    assert canonical({"b": 1, "a": 2}) == b'{"a":2,"b":1}'


def test_canonical_no_whitespace():
    assert b" " not in canonical({"a": [1, 2, 3]})


def test_hmac_signer_rejects_empty_key():
    with pytest.raises(ValueError):
        HMACVerifier(b"")


def test_sign_verify_roundtrip():
    v = HMACVerifier(KEY)
    sig = v.sign(b"payload")
    assert v.verify(b"payload", sig)


def test_verify_rejects_tampered_payload():
    v = HMACVerifier(KEY)
    sig = v.sign(b"payload")
    assert not v.verify(b"payload2", sig)


def test_verify_function_accepts_valid():
    v = HMACVerifier(KEY)
    sig = v.sign(b"payload").hex()
    result = verify(b"payload", sig, v)
    assert isinstance(result, VerificationResult)
    assert result.ok
    assert result.reason == ""


def test_verify_function_rejects_mismatch():
    v = HMACVerifier(KEY)
    result = verify(b"payload", "00" * 32, v)
    assert not result.ok
    assert "mismatch" in result.reason


def test_verify_function_rejects_malformed_hex():
    v = HMACVerifier(KEY)
    result = verify(b"payload", "zz", v)
    assert not result.ok
    assert "hex" in result.reason


def test_verify_accepts_bytes_signature():
    v = HMACVerifier(KEY)
    sig = v.sign(b"payload")
    assert verify(b"payload", sig, v).ok


def test_verify_accepts_string_payload():
    v = HMACVerifier(KEY)
    sig = v.sign(b"payload").hex()
    assert verify("payload", sig, v).ok


def test_verify_handles_verifier_exception():
    class Boom:
        def sign(self, payload):
            return b""
        def verify(self, payload, signature):
            raise RuntimeError("boom")
    result = verify(b"x", b"y", Boom())
    assert not result.ok
    assert "RuntimeError" in result.reason
