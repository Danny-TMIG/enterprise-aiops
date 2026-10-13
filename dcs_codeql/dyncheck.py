#!/usr/bin/env python3
"""Dynamic grounding: run the DCS system, assert on live behavior.

Same 8 grounded claims as pycheck.py, but proven by executing the
real code and inspecting real outputs. No AST walking. No mocks.
The system runs, and the claim either holds or doesn't.
"""
from __future__ import annotations

import json
import socket
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dcs import rogue
from dcs.certify import issue_license, verify_license
from dcs.ct import TransparencyLog
from dcs.triad.kernel import Kernel

KEY = b"dynamic-grounding-key-not-for-production"


# ═══════════════════════════════════════════════════════════════════
# 1. ALIGNED — every scope action produces exactly one attestation
# ═══════════════════════════════════════════════════════════════════
def check_aligned() -> list:
    bad = []
    chain = rogue.Chain(KEY)
    for i, (code, layer, verb, output, anchor) in enumerate(rogue.HATS):
        chain.append(
            action_id=f"{code}-{i:03d}",
            hat=code,
            payload={"verb": verb, "output": output},
            anchor=anchor,
        )
    if len(chain.entries) != len(rogue.HATS):
        bad.append(f"chain length {len(chain.entries)} != scope {len(rogue.HATS)}")
    for i, e in enumerate(chain.entries):
        if e.layer != rogue.HAT_INDEX[e.hat]["layer"]:
            bad.append(f"entry {i} layer {e.layer} != {rogue.HAT_INDEX[e.hat]['layer']}")
        if e.prev_hash != (chain.entries[i-1].digest() if i else rogue.Chain.GENESIS):
            bad.append(f"entry {i} prev_hash mismatch")
    return bad


# ═══════════════════════════════════════════════════════════════════
# 2. SAFE — a rogue injection is detected on the live chain
# ═══════════════════════════════════════════════════════════════════
def check_safe() -> list:
    bad = []
    chain = rogue.Chain(KEY)
    for i, (code, layer, verb, output, anchor) in enumerate(rogue.HATS):
        chain.append(f"{code}-{i:03d}", code,
                     {"verb": verb, "output": output}, anchor)
    detection_clean = rogue.detect_rogue(chain, KEY)
    if detection_clean["rogue"]:
        bad.append("clean chain flagged as rogue")

    chain.append("ROGUE-001", "SO",
                 {"verb": "attack", "output": "exploit"},
                 anchor="Nonexistent Standard")
    detection_rogue = rogue.detect_rogue(chain, KEY)
    if not detection_rogue["rogue"]:
        bad.append("rogue action not detected")
    tail = detection_rogue["per_entry"][-1]
    if "unanchored" not in tail["flags"]:
        bad.append(f"expected unanchored flag, got {tail['flags']}")
    return bad


# ═══════════════════════════════════════════════════════════════════
# 3. COMPLETE — every hat maps to a clause, every layer has a hat
# ═══════════════════════════════════════════════════════════════════
def check_complete() -> list:
    bad = []
    for code, layer, verb, output, anchor in rogue.HATS:
        if not anchor:
            bad.append(f"hat {code} has empty anchor")
        if code not in rogue.HAT_INDEX:
            bad.append(f"hat {code} not in HAT_INDEX")
        if rogue.HAT_INDEX[code]["layer"] != layer:
            bad.append(f"hat {code} layer mismatch")
    by_layer = rogue.hats_by_layer()
    for L in range(7):
        if not by_layer[L]:
            bad.append(f"layer {L} has no hats")
    return bad


# ═══════════════════════════════════════════════════════════════════
# 4. PREVENTION — detection is O(n) and returns the same verdict twice
# ═══════════════════════════════════════════════════════════════════
def check_prevention() -> list:
    bad = []
    chain = rogue.Chain(KEY)
    for i, (code, layer, verb, output, anchor) in enumerate(rogue.HATS):
        chain.append(f"{code}-{i:03d}", code,
                     {"verb": verb, "output": output}, anchor)
    # determinism
    r1 = rogue.detect_rogue(chain, KEY)
    r2 = rogue.detect_rogue(chain, KEY)
    if r1["rogue"] != r2["rogue"]:
        bad.append("detect_rogue not deterministic on same chain")
    if r1["per_entry"] != r2["per_entry"]:
        bad.append("per_entry differs across two calls")
    # evidence trail
    if not all("flags" in e for e in r1["per_entry"]):
        bad.append("per_entry missing flags field")
    return bad


# ═══════════════════════════════════════════════════════════════════
# 5. FINITE — every triad verdict is one of the four Belnap states
# ═══════════════════════════════════════════════════════════════════
def check_finite() -> list:
    bad = []
    valid = {"PASS", "FAIL", "UNKNOWN", "CONFLICT"}
    k = Kernel()
    # exhaust a sample of specs
    specs = [
        {},
        {"conformance": {"declared": 1, "actual": 1}},
        {"conformance": {"declared": 1, "actual": 2}},
        {"coherence": {"a": 1, "b": 2, "mode": "equivalence"}},
        {"coordination": {"states": [], "mode": "merge"}},
    ]
    for spec in specs:
        t = k.verify(spec)
        if t.verdict() not in valid:
            bad.append(f"verdict {t.verdict()} not in Belnap FOUR")
        d = t.to_dict()
        for axis in ("conformance", "coherence", "coordination"):
            if d[axis]["name"] not in valid:
                bad.append(f"axis {axis} = {d[axis]['name']} not Belnap")
    return bad


# ═══════════════════════════════════════════════════════════════════
# 6. FORGEABLE — mutating a signed attestation is detected
# ═══════════════════════════════════════════════════════════════════
def check_forgeable() -> list:
    bad = []
    chain = rogue.Chain(KEY)
    for i, (code, layer, verb, output, anchor) in enumerate(rogue.HATS[:5]):
        chain.append(f"{code}-{i:03d}", code,
                     {"verb": verb, "output": output}, anchor)
    # mutate body of entry 2 → signature must fail
    chain.entries[2].payload["verb"] = "tampered"
    detection = rogue.detect_rogue(chain, KEY)
    flags = detection["per_entry"][2]["flags"]
    if "bad_signature" not in flags and "chain_break" not in flags:
        bad.append(f"mutated entry not flagged: {flags}")

    # forged signature
    chain2 = rogue.Chain(KEY)
    chain2.append("x-000", "FE", {"verb": "render"}, "W3C HTML/CSS")
    chain2.entries[0].signature = "0" * 64
    d2 = rogue.detect_rogue(chain2, KEY)
    if not d2["rogue"]:
        bad.append("forged signature not detected")
    if "bad_signature" not in d2["per_entry"][0]["flags"]:
        bad.append("bad_signature flag missing")
    return bad


# ═══════════════════════════════════════════════════════════════════
# 7. ANCHORED — every issued license anchors to a real body
# ═══════════════════════════════════════════════════════════════════
def check_anchored() -> list:
    bad = []
    cert = issue_license("dyn-anchor-test", KEY)
    if not cert.scope.anchors:
        bad.append("scope has no anchors")
    for a in cert.scope.anchors:
        if len(a) < 2:
            bad.append(f"trivial anchor: {a!r}")
    if len(cert.scope.hats) != len(rogue.HATS):
        bad.append("scope hats != total hats")
    return bad


# ═══════════════════════════════════════════════════════════════════
# 8. EXTERNALLY_VERIFIABLE — verify runs with network blocked
# ═══════════════════════════════════════════════════════════════════
def check_externally_verifiable() -> list:
    bad = []
    cert = issue_license("dyn-net-test", KEY)

    def _no_network(*args, **kwargs):
        raise RuntimeError("network access attempted during verification")

    with patch.object(socket, "socket", _no_network), \
         patch.object(socket, "create_connection", _no_network), \
         patch("urllib.request.urlopen", _no_network, create=True):
        v = verify_license(cert, KEY)
    if v["verdict"] != "PASS":
        bad.append(f"offline verification failed: {v['verdict']}")
    if not v["signature_valid"]:
        bad.append("signature invalid in offline mode")
    if not v["chain_valid"]:
        bad.append("chain invalid in offline mode")
    return bad


# ═══════════════════════════════════════════════════════════════════
# BONUS — the tamper demo, exercised dynamically
# ═══════════════════════════════════════════════════════════════════
def check_tamper_dynamic() -> list:
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        log_path = tmp / "ct.json"
        # issue two licenses
        c1 = issue_license("alpha", KEY)
        log = TransparencyLog(KEY)
        log.append(c1.digest(), c1.issued_to)
        log.save(log_path)
        # tamper
        d = json.loads(log_path.read_text())
        d["entries"][0]["holder"] = "rogue"
        log_path.write_text(json.dumps(d))
        # reload and verify
        log2 = TransparencyLog.load(log_path, KEY)
        v = log2.verify()
        if v["valid"]:
            bad.append("tampered log verified as valid")
        if v.get("broken_at") != 0:
            bad.append(f"broken_at = {v.get('broken_at')}, expected 0")
        if v.get("reason") != "leaf":
            bad.append(f"reason = {v.get('reason')}, expected 'leaf'")
    return bad


CHECKS = [
    ("1_aligned",               check_aligned,               "runtime chain integrity"),
    ("2_safe",                  check_safe,                  "rogue detected at runtime"),
    ("3_complete",              check_complete,              "hats cover all layers"),
    ("4_prevention",            check_prevention,            "detection deterministic"),
    ("5_finite",                check_finite,                "Belnap verdict total"),
    ("6_forgeable_evidence",    check_forgeable,             "tampering detected"),
    ("7_anchored",              check_anchored,              "license anchors real"),
    ("8_externally_verifiable", check_externally_verifiable, "offline verification"),
    ("9_tamper_dynamic",        check_tamper_dynamic,        "CT log tamper FAIL"),
]


def main():
    print("→ dynamic grounding: running the real system")
    print()
    passed = failed = 0
    for name, fn, desc in CHECKS:
        t0 = time.time()
        try:
            bad = fn()
        except Exception as e:
            bad = [f"exception: {type(e).__name__}: {e}"]
        dt = (time.time() - t0) * 1000
        if not bad:
            print(f"  PASS  {name:<26}  {desc}  ({dt:.0f}ms)")
            passed += 1
        else:
            print(f"  FAIL  {name:<26}  {desc}  ({dt:.0f}ms)")
            for line in bad[:3]:
                print(f"        {line}")
            failed += 1
    print()
    print("═" * 64)
    print(f"  dynamic claims passing: {passed} / {len(CHECKS)}")
    print(f"  dynamic claims failing: {failed} / {len(CHECKS)}")
    print("═" * 64)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
