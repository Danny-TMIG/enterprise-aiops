import pytest
from dcs.evidence_chain import generate_evidence_claim, verify_evidence_claim
from dcs.sdlc_engine import SdlcEngine
from dcs.qualify_evidence import qualify_process
from dcs.verify_evidence import re_verify_record

def test_evidence_chain_complete_pass_flow():
    claim = generate_evidence_claim("SDLC-0001", "dcs/self.py", "dcs/tests/test_pytest_mastery.py", "VERIFYING_0001\n", 0)
    assert verify_evidence_claim(claim, "VERIFYING_0001\n", 0) == "PASS"

def test_evidence_chain_partial_mismatch_flow():
    claim = generate_evidence_claim("SDLC-0001", "dcs/self.py", "dcs/tests/test_pytest_mastery.py", "VERIFYING_0001\n", 0)
    assert verify_evidence_claim(claim, "VERIFYING_0001\n", 0, fresh_impl_hash="altered") == "PARTIAL"

def test_evidence_chain_blocked_signature_tamper():
    claim = generate_evidence_claim("SDLC-0001", "dcs/self.py", "dcs/tests/test_pytest_mastery.py", "VERIFYING_0001\n", 0)
    claim["signature"] = "tampered"
    assert verify_evidence_claim(claim, "VERIFYING_0001\n", 0) == "BLOCKED"

def test_sdlc_engine_empty_manifest():
    assert SdlcEngine("non_existent.json").load_manifest() == []

def test_sdlc_engine_uke_mapping_axis():
    assert SdlcEngine().map_to_uke_primitive("SDLC-0001", "G01")["status"] == "MAPPING_VERIFIED"