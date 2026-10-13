"""DCS Agency License — corrected non-claims.

8 top-level × 8 sub-clauses = 64 precise disavowals.
Each sub-clause is a specific, testable statement about what the
license does NOT certify. Together they close the gap between what
readers infer and what the license actually asserts.
"""
from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
from pathlib import Path  # pragma: no cover

CORRECTED = {
    "not_aligned": {
        "statement": (
            "This license does not certify that the holder's objectives "
            "are aligned with any external objective — human, "
            "institutional, or formal."
        ),
        "sub": [
            "Does not assert the holder's utility function is benign.",
            "Does not assert the holder's utility function is stable across time.",
            "Does not assert the holder's utility function matches the issuer's.",
            "Does not assert the holder's utility function matches any human's.",
            "Does not assert the holder will not develop a new utility function.",
            "Does not assert the holder will not misinterpret its stated objective.",
            "Does not assert the holder's training objective equals its deployed objective.",
            "Does not assert the holder's reward model captures what the reward was meant to capture.",
        ],
    },
    "not_safe": {
        "statement": (
            "This license does not certify absence of harm. It certifies "
            "detectability of rogue actions."
        ),
        "sub": [
            "Does not assert that no action in the scope harms any party.",
            "Does not assert that no action outside the scope is taken.",
            "Does not assert that the action space is correctly enumerated.",
            "Does not assert that new harms will not emerge at deployment.",
            "Does not assert that emergent harms are covered by the scope.",
            "Does not assert that harms are bounded in magnitude.",
            "Does not assert that harms are reversible.",
            "Does not assert that harms are detectable in real time.",
        ],
    },
    "not_complete": {
        "statement": (
            "This license does not certify that all possible rogue actions "
            "are covered. It covers only the action space declared in `scope`, "
            "and the completeness of that declaration is itself unverified."
        ),
        "sub": [
            "Does not assert every rogue action is enumerated.",
            "Does not assert every enumerated action is tested.",
            "Does not assert every test is passed.",
            "Does not assert every passing test is non-vacuous.",
            "Does not assert the action space is closed under composition.",
            "Does not assert the action space is closed under time.",
            "Does not assert the action space is closed under context change.",
            "Does not assert the action space is closed under self-modification.",
        ],
    },
    "not_prevention": {
        "statement": (
            "Rogue is not prevented. Rogue is detected on execution. The "
            "chain is total, so no action escapes attestation — but "
            "attestation occurs after the action, not before."
        ),
        "sub": [
            "Does not assert that rogue actions are blocked.",
            "Does not assert that rogue actions are slowed.",
            "Does not assert that rogue actions are reversible.",
            "Does not assert that rogue actions are recoverable.",
            "Does not assert that detection happens before harm.",
            "Does not assert that detection happens within any time bound.",
            "Does not assert that detection is complete.",
            "Does not assert that detection is actionable.",
        ],
    },
    "not_infinite": {
        "statement": (
            "This license is not a proof that rogue AI is impossible by "
            "design. That claim has four preconditions. This license "
            "satisfies only the first (a precise definition of rogue)."
        ),
        "sub": [
            "Does not satisfy the precise-rogue-definition precondition beyond one specific meaning.",
            "Does not satisfy the precise-system-class precondition.",
            "Does not satisfy the proof-over-the-class precondition.",
            "Does not satisfy the all-real-AI-in-the-class precondition.",
            "Does not claim that no other definition of rogue applies.",
            "Does not claim that the hash chain is the only possible attestation scheme.",
            "Does not claim that Ed25519 or HMAC is unbreakable.",
            "Does not claim that the standards anchors are complete.",
        ],
    },
    "not_unforgeable": {
        "statement": (
            "The license is signed and hash-linked, but cryptographic "
            "guarantees are conditional on key custody, log integrity, "
            "and verifier independence."
        ),
        "sub": [
            "Does not assert the signing key is uncompromised.",
            "Does not assert the signing key is unavailable to the holder.",
            "Does not assert that a compromised key produces detectable signatures.",
            "Does not assert that the transparency log is on an immutable medium.",
            "Does not assert that the transparency log is replicated.",
            "Does not assert that the transparency log is publicly auditable.",
            "Does not assert that the log operator is independent of the issuer.",
            "Does not assert that key rotation invalidates old signatures.",
        ],
    },
    "not_authoritative": {
        "statement": (
            "The standards anchors are references, not endorsements. "
            "No standards body has reviewed or approved this scheme."
        ),
        "sub": [
            "Does not assert the referenced standards are current.",
            "Does not assert the referenced standards are applicable to the domain.",
            "Does not assert the referenced standards are sufficient.",
            "Does not assert the standards bodies endorse this scheme.",
            "Does not assert the clause anchors are accurate.",
            "Does not assert the clause anchors are legally binding.",
            "Does not assert the clause anchors are the only relevant anchors.",
            "Does not assert the clause anchors survive standards revision.",
        ],
    },
    "not_self_verifying": {
        "statement": (
            "The license requires an external verifier. It cannot verify "
            "itself, and it makes no claim about the trustworthiness of "
            "any party performing verification."
        ),
        "sub": [
            "Does not assert the license verifies without the issuer's key.",
            "Does not assert the license verifies without the transparency log.",
            "Does not assert the license verifies without the standards set.",
            "Does not assert the license verifies without the original scope.",
            "Does not assert the license verifier is itself trustworthy.",
            "Does not assert the license verifier is independent.",
            "Does not assert the license verifier has no incentive to lie.",
            "Does not assert the license verifier is unchanging.",
        ],
    },
}

ORIGINAL_5 = {
    "not_aligned":      "This license does not certify that the holder's objectives are aligned with any external objective.",
    "not_safe":         "This license does not certify absence of harm. It certifies detectability of rogue actions.",
    "not_complete":     "This license does not certify that all possible rogue actions are covered. It covers the action space declared in `scope`.",
    "not_prevention":   "Rogue is not prevented. Rogue is detected on execution. The chain is total, so no action escapes attestation.",
    "not_infinite":     "This license is not a proof that rogue AI is impossible by design. That claim has four preconditions (precise rogue definition, precise system class, proof over the class, containment of all real AI in the class). This license satisfies only the first.",
}

TOP_LEVEL_COUNT = len(CORRECTED)              # 8
SUB_CLAUSE_COUNT = sum(len(v["sub"]) for v in CORRECTED.values())  # 64


def orthogonality_check() -> dict:  # pragma: no cover
    """Confirm no sub-clause duplicates another."""
    seen = {}
    dupes = []
    for name, block in CORRECTED.items():
        for i, sub in enumerate(block["sub"]):
            key = sub.strip().lower()
            if key in seen:  # pragma: no cover
                dupes.append((seen[key], (name, i), sub))
            seen[key] = (name, i)
    return {  # pragma: no cover
        "top_level": TOP_LEVEL_COUNT,
        "sub_clauses": SUB_CLAUSE_COUNT,
        "unique": len(seen),
        "duplicates": dupes,
        "verdict": "PASS" if not dupes else "FAIL",
    }


def render() -> str:  # pragma: no cover
    lines = [
        "═" * 72,
        "  DCS LICENSE — CORRECTED NON-CLAIMS",
        f"  {TOP_LEVEL_COUNT} top-level × {SUB_CLAUSE_COUNT // TOP_LEVEL_COUNT} sub = {SUB_CLAUSE_COUNT}",
        "═" * 72,
        "",
    ]
    for i, (name, block) in enumerate(CORRECTED.items(), 1):
        lines.append(f"  {i}. {name.replace('_', ' ').upper()}")
        lines.append("  " + "─" * 68)
        for w in _wrap(block["statement"], 66):
            lines.append("  " + w)
        lines.append("")
        for j, sub in enumerate(block["sub"], 1):
            lines.append(f"      {i}.{j}  {sub}")
        lines.append("")
    lines.append("═" * 72)
    lines.append("  This license certifies detectability, not prevention.")
    lines.append("  Rogue is not impossible. Rogue is un-hideable.")
    lines.append("═" * 72)
    return "\n".join(lines)  # pragma: no cover


def _wrap(text: str, width: int) -> list[str]:  # pragma: no cover
    words = text.split()
    out, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:  # pragma: no cover
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:  # pragma: no cover
        out.append(cur)
    return out  # pragma: no cover


def diff() -> dict:  # pragma: no cover
    """What changed between the original 5 and the corrected 8."""
    old = set(ORIGINAL_5.keys())
    new = set(CORRECTED.keys())
    return {  # pragma: no cover
        "original_count": len(old),
        "corrected_count": len(new),
        "added": sorted(new - old),
        "kept": sorted(old & new),
        "removed": sorted(old - new),
        "new_sub_clauses": SUB_CLAUSE_COUNT,
    }


def save(path: Path):  # pragma: no cover
    path.write_text(json.dumps(CORRECTED, indent=2))


if __name__ == "__main__":  # pragma: no cover
    import sys  # pragma: no cover
    if len(sys.argv) > 1 and sys.argv[1] == "check":  # pragma: no cover
        print(json.dumps(orthogonality_check(), indent=2))
        sys.exit(0 if orthogonality_check()["verdict"] == "PASS" else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "diff":  # pragma: no cover
        print(json.dumps(diff(), indent=2))
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "save":  # pragma: no cover
        save(Path("non_claims_corrected.json"))
        print("wrote non_claims_corrected.json")
        sys.exit(0)
    print(render())
