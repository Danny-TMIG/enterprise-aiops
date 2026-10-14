"""Bisimulation differential: dcs.verify under two nacl regimes.

World A: nacl importable   -> _NACL = True   (dcs/verify.py line 15)
World B: nacl not importable -> _NACL = False (line 17)

We build both worlds in-process by faking sys.modules["nacl"] before
reloading dcs.verify. After each world we restore the real module.
"""
import importlib
import json
import sys
import types
from unittest.mock import patch

import dcs.verify as v


def _bundle(**extra):
    d = {"standard_ref": "s", "reference": "r",
         "started": 1, "completed": 2,
         "results": [], "verdict": "PASS", "digest": "abc"}
    d.update(extra)
    return d


def _with_fake_nacl(fn):
    """Run fn() with a fake nacl in sys.modules, restore afterwards."""
    fake_nacl = types.ModuleType("nacl")
    fake_signing = types.ModuleType("nacl.signing")
    class _VK:
        def __init__(self, key):
            self.key = key
        def verify(self, sig, msg):
            return None
    fake_signing.VerifyKey = _VK
    fake_nacl.signing = fake_signing
    saved = {k: sys.modules.get(k) for k in ("nacl", "nacl.signing")}
    try:
        sys.modules["nacl"] = fake_nacl
        sys.modules["nacl.signing"] = fake_signing
        return fn()
    finally:
        for k, mod in saved.items():
            if mod is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = mod
        importlib.reload(v)


def _with_blocked_nacl(fn):
    """Run fn() with nacl blocked in sys.modules, restore afterwards."""
    saved = {k: sys.modules.get(k) for k in ("nacl", "nacl.signing")}
    try:
        sys.modules["nacl"] = None
        sys.modules["nacl.signing"] = None
        return fn()
    finally:
        for k, mod in saved.items():
            if mod is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = mod
        importlib.reload(v)


# ─── World A: nacl present ───────────────────────────────────────────
def test_nacl_present_sets_true():
    """Covers dcs/verify.py line 15 (_NACL = True)."""
    def run():
        importlib.reload(v)
        assert v._NACL is True
    _with_fake_nacl(run)


def test_nacl_present_signature_block(tmp_path):
    """Covers lines 32-37 with the fake VerifyKey."""
    def run():
        importlib.reload(v)
        b = tmp_path / "b.json"
        b.write_text(json.dumps(_bundle(signature="00", public_key="00")))
        with patch.object(v, "digest_of", return_value="abc"), \
             patch.object(v, "canonical", return_value=b"x"):
            r = v.verify(b, tmp_path / "std", tmp_path, re_run=False)
        assert r["signature_ok"] is True
    _with_fake_nacl(run)


def test_nacl_present_signature_block_failure(tmp_path):
    """Covers lines 32-37 with a failing VerifyKey (sig_ok=False)."""
    def run():
        importlib.reload(v)
        # Replace VerifyKey with one that raises on verify
        sys.modules["nacl.signing"].VerifyKey = type(
            "VK", (), {"__init__": lambda self, k: None,
                        "verify": lambda self, s, m: (_ for _ in ()).throw(Exception("bad"))})
        b = tmp_path / "b.json"
        b.write_text(json.dumps(_bundle(signature="00", public_key="00")))
        with patch.object(v, "digest_of", return_value="abc"), \
             patch.object(v, "canonical", return_value=b"x"):
            r = v.verify(b, tmp_path / "std", tmp_path, re_run=False)
        assert r["signature_ok"] is False
    _with_fake_nacl(run)


# ─── World B: nacl blocked ───────────────────────────────────────────
def test_nacl_absent_sets_false():
    """Covers dcs/verify.py line 17 (_NACL = False)."""
    def run():
        importlib.reload(v)
        assert v._NACL is False
    _with_blocked_nacl(run)


def test_nacl_absent_signature_block_skipped(tmp_path):
    """With _NACL=False, the signature block is skipped entirely."""
    def run():
        importlib.reload(v)
        b = tmp_path / "b.json"
        b.write_text(json.dumps(_bundle(signature="00", public_key="00")))
        with patch.object(v, "digest_of", return_value="abc"), \
             patch.object(v, "canonical", return_value=b"x"):
            r = v.verify(b, tmp_path / "std", tmp_path, re_run=False)
        assert r["signature_ok"] is None
    _with_blocked_nacl(run)


# ─── Bisimulation: same observable in both worlds ────────────────────
def test_bisimulation_no_signature(tmp_path):
    """Bundle without a signature: both worlds return signature_ok=None."""
    b = tmp_path / "b.json"
    b.write_text(json.dumps(_bundle()))

    def run_a():
        importlib.reload(v)
        with patch.object(v, "digest_of", return_value="abc"), \
             patch.object(v, "canonical", return_value=b"x"):
            return v.verify(b, tmp_path / "std", tmp_path, re_run=False)

    def run_b():
        importlib.reload(v)
        with patch.object(v, "digest_of", return_value="abc"), \
             patch.object(v, "canonical", return_value=b"x"):
            return v.verify(b, tmp_path / "std", tmp_path, re_run=False)

    a = _with_fake_nacl(run_a)
    b_ = _with_blocked_nacl(run_b)
    assert a["signature_ok"] is None
    assert b_["signature_ok"] is None
    assert a["integrity"] == b_["integrity"]
    assert a["verdict"] == b_["verdict"]
    assert a["replay"] == b_["replay"]
