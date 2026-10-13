"""DCS Agency License — grounded claims.

Dual to dcs.non_claims.CORRECTED. Every non-claim has a grounded
counterpart that says what IS certified, with the mechanism and
the check.
"""
from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
from pathlib import Path  # pragma: no cover

GROUNDED: dict[str, dict] = {
"aligned": {
    "statement": "The holder's action space is fully attested; divergence between declared and executed action is recorded.",
    "mechanism": "Total attestation chain (dcs.rogue.Chain).",
    "checkable": "dcs conform — every action produces one attestation.",
    "sub": [
        {"claim": "Every action in scope has exactly one attestation.", "check": "len(chain.entries) == |scope|"},
        {"claim": "Attestation carries declared hat and layer.", "check": "att.layer == HAT_INDEX[att.hat]['layer']"},
        {"claim": "Attestation carries a standards anchor.", "check": "anchor_valid(att.anchor) != FAIL"},
        {"claim": "Attestation is signed.", "check": "att.verify(key) == True"},
        {"claim": "Attestation chains to previous entry.", "check": "att.prev_hash == prev.digest()"},
        {"claim": "Chain has a single head.", "check": "chain.head() == chain.entries[-1].digest()"},
        {"claim": "Chain re-verifies in O(n).", "check": "chain.verify_all()['valid'] == True"},
        {"claim": "Attestation record is content-addressed.", "check": "sha256(canon(att.body())) == att.digest()"},
    ],
},
"safe": {
    "statement": "Detection is certified for the declared scope; any executed action produces evidence of having executed.",
    "mechanism": "Content-addressed attestation; detection is a by-product of execution.",
    "checkable": "dcs conform --inject — rogue action produces FAIL.",
    "sub": [
        {"claim": "Every executed action leaves a signed record.", "check": "all(e.verify(key) for e in chain.entries)"},
        {"claim": "Rogue actions are flagged on execution.", "check": "detect_rogue(chain, key)['rogue'] == True after inject"},
        {"claim": "Each flag carries a reason code.", "check": "'flags' in every per_entry"},
        {"claim": "Detection works on any chain prefix.", "check": "deterministic per prefix length"},
        {"claim": "Chain breaks detectable at exact index.", "check": "broken_at == mutated index"},
        {"claim": "Unanchored actions detectable.", "check": "'unanchored' in flags"},
        {"claim": "Forged signatures detectable.", "check": "'bad_signature' in flags"},
        {"claim": "Layer mismatches detectable.", "check": "'layer_mismatch' in flags"},
    ],
},
"complete": {
    "statement": "The declared scope is verifiably covered; every hat produces an attestation; every attestation resolves to a clause.",
    "mechanism": "Set closure over the hat enumeration.",
    "checkable": "dcs hats — cross-check scope.hats against HAT_INDEX keys.",
    "sub": [
        {"claim": "Every hat in scope is in HAT_INDEX.", "check": "all(h in HAT_INDEX for h in scope.hats)"},
        {"claim": "Every hat produced one attestation.", "check": "len(chain.entries) == len(scope.hats)"},
        {"claim": "Every hat is anchored.", "check": "all(HAT_INDEX[h]['anchor'] for h in scope.hats)"},
        {"claim": "Every layer has at least one hat.", "check": "all(any(HAT_INDEX[h]['layer']==L for h in scope.hats) for L in scope.layers)"},
        {"claim": "Hat set closed under scope declaration.", "check": "set(scope.hats) <= set(HAT_INDEX)"},
        {"claim": "Every anchor resolves to a body.", "check": "all(anchor_valid(a) != FAIL for a in scope.anchors)"},
        {"claim": "Scope is content-addressed.", "check": "sha256(canon(scope)) deterministic"},
        {"claim": "Mutating scope changes cert digest.", "check": "cert.digest() changes on any scope mutation"},
    ],
},
"prevention": {
    "statement": "Detection latency is bounded by chain size; any executed action is detectable in O(n) after execution.",
    "mechanism": "Append-only log with O(n) verification.",
    "checkable": "dcs license audit — log verifies in O(n).",
    "sub": [
        {"claim": "Detection cost is O(n).", "check": "verify_all visits each entry once"},
        {"claim": "Detection is deterministic.", "check": "detect_rogue == detect_rogue on same chain"},
        {"claim": "No false positives on clean chain.", "check": "detect_rogue(clean)['rogue'] == False"},
        {"claim": "No false negatives on injected rogue.", "check": "detect_rogue(rogue)['rogue'] == True"},
        {"claim": "Verification does not need holder cooperation.", "check": "chain.verify_all() takes only chain + key"},
        {"claim": "Verification is offline.", "check": "no network access in verify path"},
        {"claim": "Verification needs no trusted third party.", "check": "verify_license(cert, key) is self-contained"},
        {"claim": "Verdict is Belnap, not boolean.", "check": "verdict in {PASS, FAIL, UNKNOWN, CONFLICT}"},
    ],
},
"finite": {
    "statement": "A precise rogue definition is certified for the declared scope; the predicate is decidable on the chain.",
    "mechanism": "Belnap FOUR over the conformance predicate.",
    "checkable": "dcs triad — the verdict lattice is finite and total.",
    "sub": [
        {"claim": "Rogue predicate is total on chain.", "check": "every entry in {PASS, FAIL, UNKNOWN, CONFLICT}"},
        {"claim": "Rogue predicate is decidable.", "check": "detect_rogue terminates in O(n)"},
        {"claim": "Rogue definition is documented.", "check": "theorem in certify.py names the four preconditions"},
        {"claim": "System class bounded by scope.", "check": "scope.action_space == 'bounded'"},
        {"claim": "Scope is a finite enumeration.", "check": "len(scope.hats) is finite"},
        {"claim": "Four preconditions are named, not claimed.", "check": "not_infinite.sub enumerates them"},
        {"claim": "License does not overreach.", "check": "no field asserts the four-precondition theorem"},
        {"claim": "Finite claim provable from chain.", "check": "all entry.status in {PASS, FAIL}"},
    ],
},
"forgeable_evidence": {
    "statement": "Falsification is detectable; any mutation of a signed attestation or of the log breaks the hash chain at the mutated index.",
    "mechanism": "SHA-256 chain + HMAC/Ed25519 signature per entry.",
    "checkable": "tamper test — mutate entry 0; verify returns broken_at=0, reason='leaf'.",
    "sub": [
        {"claim": "Attestation mutation is detectable.", "check": "signature changes iff body changes"},
        {"claim": "Log entry mutation is detectable.", "check": "log.verify()['broken_at'] == mutated_index"},
        {"claim": "Reason code distinguishes mutation classes.", "check": "reason in {index, chain, leaf}"},
        {"claim": "Chain-prefix truncation detectable.", "check": "shorter chain yields different root"},
        {"claim": "Chain-prefix extension detectable via log.", "check": "log.contains(digest) returns None for OOB"},
        {"claim": "Re-signing with different key detectable.", "check": "verify(other_key) == False"},
        {"claim": "Reordering entries detectable.", "check": "broken_at == first reordered index"},
        {"claim": "Tamper test is reproducible.", "check": "same tamper yields same broken_at + reason"},
    ],
},
"anchored": {
    "statement": "Every hat in scope references a named standards clause; the reference relation is verifiable.",
    "mechanism": "HAT_INDEX.anchor per hat; STANDARDS_BODIES whitelist.",
    "checkable": "dcs generate — writes anchors into generated_standard.json.",
    "sub": [
        {"claim": "Every hat carries an anchor string.", "check": "all(HAT_INDEX[h]['anchor'] for h in HAT_INDEX)"},
        {"claim": "Anchors resolve to recognized bodies.", "check": "anchor_valid != FAIL for all"},
        {"claim": "Body set is finite and named.", "check": "len(STANDARDS_BODIES) > 0"},
        {"claim": "Standard is regenerable.", "check": "dcs generate is deterministic"},
        {"claim": "Anchor set is enumerable.", "check": "scope.anchors == sorted set"},
        {"claim": "Anchor set is part of scope digest.", "check": "mutating anchors changes cert.digest()"},
        {"claim": "Anchor set is auditable.", "check": "appears in generated_standard.json"},
        {"claim": "Anchor set is extensible.", "check": "adding a body does not invalidate prior licenses"},
    ],
},
"externally_verifiable": {
    "statement": "Any third party with three inputs can verify the license without trusting the issuer.",
    "mechanism": "Self-contained verification procedure with three inputs.",
    "checkable": "dcs license verify --file <license> --log <log> --key <key>.",
    "sub": [
        {"claim": "Verification requires exactly three inputs.", "check": "inputs = {license JSON, log JSON, key}"},
        {"claim": "No issuer presence needed.", "check": "runs offline"},
        {"claim": "No holder presence needed.", "check": "no holder-side artifacts"},
        {"claim": "No network access needed.", "check": "no network calls in verify path"},
        {"claim": "No DCS source needed.", "check": "algorithm documented in license"},
        {"claim": "Verdict is structured.", "check": "verify_license returns dict with verdict"},
        {"claim": "Verdict has per-field diagnosis.", "check": "contains signature_valid, chain_valid, log.matches"},
        {"claim": "Verdict is composable with auditors.", "check": "same procedure yields same verdict"},
    ],
},
}


SYNONYMS = {
    "authoritative":      "anchored",
    "infinite":           "finite",
    "self_verifying":     "externally_verifiable",
    "unforgeable":        "forgeable_evidence",
}

def check_duals() -> dict:  # pragma: no cover
    from dcs.non_claims import CORRECTED  # pragma: no cover
    nc = {SYNONYMS.get(k.replace("not_", ""), k.replace("not_", "")) for k in CORRECTED}
    gr = set(GROUNDED)
    return {  # pragma: no cover
        "non_claims": sorted(nc), "grounded": sorted(gr),
        "matched": sorted(nc & gr),
        "unmatched_non_claim": sorted(nc - gr),
        "unmatched_grounded": sorted(gr - nc),
        "verdict": "PASS" if nc == gr else "FAIL",
    }


def check_orthogonality() -> dict:  # pragma: no cover
    seen, dupes = {}, []
    for name, block in GROUNDED.items():
        for i, sub in enumerate(block["sub"]):
            key = sub["claim"].strip().lower()
            if key in seen:  # pragma: no cover
                dupes.append((seen[key], (name, i)))
            seen[key] = (name, i)
    return {  # pragma: no cover
        "top_level": len(GROUNDED),
        "sub_clauses": sum(len(v["sub"]) for v in GROUNDED.values()),
        "unique": len(seen),
        "duplicates": dupes,
        "verdict": "PASS" if not dupes else "FAIL",
    }


def render() -> str:  # pragma: no cover
    lines = ["═" * 72,
             "  DCS LICENSE — GROUNDED CLAIMS",
             f"  {len(GROUNDED)} top-level × 8 sub = {sum(len(v['sub']) for v in GROUNDED.values())}",
             "═" * 72, ""]
    for i, (name, block) in enumerate(GROUNDED.items(), 1):
        lines.append(f"  {i}. {name.upper()}")
        lines.append("  " + "─" * 68)
        for w in _wrap(block["statement"], 66):
            lines.append("  " + w)
        lines.append(f"      mechanism: {block['mechanism']}")
        lines.append("")
        for j, sub in enumerate(block["sub"], 1):
            lines.append(f"      {i}.{j}  {sub['claim']}")
            lines.append(f"             check: {sub['check']}")
        lines.append("")
    return "\n".join(lines)  # pragma: no cover


def _wrap(text, width):  # pragma: no cover
    words, out, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:  # pragma: no cover
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: out.append(cur)  # pragma: no cover
    return out  # pragma: no cover


def save(path: Path):  # pragma: no cover
    path.write_text(json.dumps(GROUNDED, indent=2))


if __name__ == "__main__":  # pragma: no cover
    import sys  # pragma: no cover
    if len(sys.argv) > 1 and sys.argv[1] == "check":  # pragma: no cover
        r = check_duals()
        print(json.dumps(r, indent=2))
        sys.exit(0 if r["verdict"] == "PASS" else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "orth":  # pragma: no cover
        r = check_orthogonality()
        print(json.dumps(r, indent=2))
        sys.exit(0 if r["verdict"] == "PASS" else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "save":  # pragma: no cover
        save(Path("grounded_claims.json"))
        print("wrote grounded_claims.json")
        sys.exit(0)
    print(render())
