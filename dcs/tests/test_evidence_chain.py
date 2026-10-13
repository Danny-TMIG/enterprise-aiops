"""Tests for the evidence chain module."""
import json
from pathlib import Path

from dcs.evidence_chain import (
    BLOCKED,
    FAIL,
    PARTIAL,
    PASS,
    EvidenceChain,
    EvidenceRecord,
    _file_sha,
    _sha,
)

HERE = Path(__file__).resolve().parent
IMPL = HERE.parent / "evidence_chain.py"
IMPL_STR = str(IMPL)


def _mkchain(tmp_path):
    return EvidenceChain(tmp_path / "store")


def test_sha_and_file_sha(tmp_path):
    assert _sha(b"abc") == _sha(b"abc")
    p = tmp_path / "x.bin"
    p.write_bytes(b"hello")
    assert _file_sha(p) == _sha(b"hello")


def test_record_roundtrip():
    r = EvidenceRecord(id="abc", result=PASS, foo=1)
    assert r.id == "abc"
    assert r.result == PASS
    assert json.loads(r.to_json())["foo"] == 1
    r2 = EvidenceRecord.from_json(r.to_json())
    assert r2.data == r.data


def test_chain_init(tmp_path):
    c = _mkchain(tmp_path)
    assert c.store.exists()


def test_capture_success(tmp_path):
    c = _mkchain(tmp_path)
    rec = c.capture(
        claim="print ok", requirement_ref="R-1",
        implementation=IMPL, test=Path(__file__),
        command=".venv/bin/python -c \"print('ok')\"",
    )
    assert rec.result == PASS
    assert rec.data["observation"]["returncode"] == 0
    assert rec.data["id"]


def test_capture_failure(tmp_path):
    c = _mkchain(tmp_path)
    rec = c.capture(
        claim="exit 1", requirement_ref="R-2",
        implementation=IMPL, test=Path(__file__),
        command=".venv/bin/python -c \"import sys; sys.exit(1)\"",
    )
    assert rec.result == FAIL
    assert rec.data["observation"]["returncode"] == 1


def test_capture_timeout(tmp_path):
    c = _mkchain(tmp_path)
    rec = c.capture(
        claim="sleep", requirement_ref="R-3",
        implementation=IMPL, test=Path(__file__),
        command="sleep 5", timeout=1,
    )
    assert rec.result == BLOCKED


def test_verify_pass(tmp_path):
    c = _mkchain(tmp_path)
    rec = c.capture(
        claim="print ok", requirement_ref="R-1",
        implementation=IMPL, test=Path(__file__),
        command=".venv/bin/python -c \"print('ok')\"",
    )
    v = c.verify(rec)
    assert v.data["verification_result"] == PASS


def test_verify_partial_after_tamper(tmp_path):
    c = _mkchain(tmp_path)
    copy = tmp_path / "impl.py"
    copy.write_text(IMPL.read_text())
    rec = c.capture(
        claim="print ok", requirement_ref="R-1",
        implementation=copy, test=Path(__file__),
        command=".venv/bin/python -c \"print('ok')\"",
    )
    copy.write_text("tampered")
    v = c.verify(rec)
    assert v.data["verification_result"] == PARTIAL


def test_verify_no_observation(tmp_path):
    c = _mkchain(tmp_path)
    rec = c.capture(
        claim="sleep", requirement_ref="R-3",
        implementation=IMPL, test=Path(__file__),
        command="sleep 5", timeout=1,
    )
    v = c.verify(rec)
    assert v.data["verification_result"] == PARTIAL


def test_sign_and_verify_signature(tmp_path):
    c = _mkchain(tmp_path)
    rec = c.capture(
        claim="print ok", requirement_ref="R-1",
        implementation=IMPL, test=Path(__file__),
        command=".venv/bin/python -c \"print('ok')\"",
    )
    key = "aa" * 32
    c.sign(rec, key)
    assert c.verify_signature(rec, key) is True
    assert c.verify_signature(rec, "bb" * 32) is False


def test_store_and_load(tmp_path):
    c = _mkchain(tmp_path)
    rec = c.capture(
        claim="print ok", requirement_ref="R-1",
        implementation=IMPL, test=Path(__file__),
        command=".venv/bin/python -c \"print('ok')\"",
    )
    p = c.store_record(rec, "rec.json")
    assert p.exists()
    r2 = c.load_record("rec.json")
    assert r2.id == rec.id
