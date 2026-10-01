"""Third-party verification of an evidence bundle."""
from __future__ import annotations
import json
from pathlib import Path

from dcs.conform import run
from dcs.evidence import canonical, digest_of
from dcs.standard import load

try:
    import nacl.signing  # type: ignore
    _NACL = True
except Exception:
    _NACL = False


def verify(bundle_path: Path, standard_path: Path, root: Path,
           *, re_run: bool = True) -> dict:
    raw = json.loads(bundle_path.read_text())

    # 1. structural integrity
    claimed = raw.get("digest")
    unsigned = {k: raw[k] for k in
                ("standard_ref", "reference", "started", "completed", "results")}
    actual = digest_of(unsigned)
    integrity = (claimed == actual)

    # 2. signature (if present and nacl available)
    sig_ok = None
    if raw.get("signature") and raw.get("public_key") and _NACL:
        try:
            vk = nacl.signing.VerifyKey(bytes.fromhex(raw["public_key"]))
            vk.verify(canonical(unsigned), bytes.fromhex(raw["signature"]))
            sig_ok = True
        except Exception:
            sig_ok = False

    # 3. optional replay
    replay = None
    if re_run:
        standard = load(standard_path)
        fresh = run(standard, root)
        replay = {
            "fresh_verdict": fresh.verdict(),
            "matches_claimed": fresh.verdict() == raw.get("verdict"),
            "results_equal": (
                [r.to_dict() for r in fresh.results] == raw.get("results")
            ),
        }

    return {
        "integrity": integrity,
        "signature_ok": sig_ok,
        "replay": replay,
        "verdict": raw.get("verdict"),
    }
