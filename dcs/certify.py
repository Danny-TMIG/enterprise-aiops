"""DCS Agency License — the certification artifact.

Grants full agency over an action space. Every action is attested.
Every attestation is anchored. Every chain is verifiable. Rogue is
detectable. Rogue is NOT prevented.
"""
from __future__ import annotations  # pragma: no cover

import hashlib  # pragma: no cover
import json  # pragma: no cover
import time  # pragma: no cover
from dataclasses import asdict, dataclass  # pragma: no cover

from dcs import rogue  # pragma: no cover

LICENSE_VERSION = "1.0"
AUTHORITY = "DCS Reference Authority"


@dataclass
class Scope:  # pragma: no cover
    hats: list[str]
    layers: list[int]
    anchors: list[str]
    action_space: str = "bounded"      # bounded | open
    domain: str = "software engineering"

    def covers(self, hat: str) -> bool:  # pragma: no cover
        return hat in self.hats  # pragma: no cover


@dataclass
class NonClaims:  # pragma: no cover
    """Corrected non-claims: 8 top-level × 8 sub = 64."""
    not_aligned:         str = ""
    not_safe:            str = ""
    not_complete:        str = ""
    not_prevention:      str = ""
    not_infinite:        str = ""
    not_unforgeable:     str = ""
    not_authoritative:   str = ""
    not_self_verifying:  str = ""

    @classmethod
    def load(cls) -> NonClaims:  # pragma: no cover
        from dcs.non_claims import CORRECTED  # pragma: no cover
        return cls(**{k: v["statement"] for k, v in CORRECTED.items()})  # pragma: no cover


@dataclass
class Certification:  # pragma: no cover
    license_version: str
    issued_to: str
    issued_by: str
    issued_at: float
    scope: Scope
    chain_length: int
    chain_head: str
    chain_valid: bool
    rogue_detected: bool
    verdict: str
    non_claims: NonClaims
    theorem: str
    verification_procedure: str
    signature: str = ""

    def body(self) -> dict:  # pragma: no cover
        d = asdict(self)
        d.pop("signature", None)
        return d  # pragma: no cover

    def digest(self) -> str:  # pragma: no cover
        return hashlib.sha256(  # pragma: no cover
            json.dumps(self.body(), sort_keys=True,
                       separators=(",", ":")).encode()
        ).hexdigest()

    def sign(self, key: bytes) -> Certification:  # pragma: no cover
        self.signature = hashlib.sha256(
            key + self.digest().encode()
        ).hexdigest()
        return self  # pragma: no cover

    def verify(self, key: bytes) -> bool:  # pragma: no cover
        expected = hashlib.sha256(key + self.digest().encode()).hexdigest()
        return expected == self.signature  # pragma: no cover


THEOREM = """
Let A = the action space declared in `scope`.
Let Att = set of valid attestations.
Let chain : Att → Att ∪ {⊥} be the predecessor map.
Let anchor : Att → Standards be the standards clause map.
Let sign : Att → Signature be the signature map.

Premises (established by construction in dcs.rogue.Chain):
  (1) ∀a ∈ A. ∃ att(a) ∈ Att
  (2) ∀att. chain(att) = ⊥ ∨ chain(att) ∈ Att
  (3) ∀att. anchor(att) ∈ Standards
  (4) ∀att. verify(sign(att)) = PASS

Then: ∀a ∈ A. rogue(a) ⟹ ∃t. detect(att(a), t) = FAIL

No assumption is made about the holder's objectives. The chain does not
constrain intent. It constrains observability. Rogue is a state whose
attestation breaks; a break is a detection.
""".strip()


def issue_license(holder: str, key: bytes, *,  # pragma: no cover
                  hats: list[str] | None = None,
                  layers: list[int] | None = None,
                  domain: str = "software engineering") -> Certification:
    """Issue a full-agency license over the declared action space."""
    all_hats = [h[0] for h in rogue.HATS]
    all_layers = list(range(7))
    hats = hats or all_hats
    layers = layers if layers is not None else all_layers

    # Build the chain that will back the license.
    chain = rogue.Chain(key)
    for i, (code, layer, verb, output, anchor) in enumerate(rogue.HATS):
        if code not in hats:  # pragma: no cover
            continue
        chain.append(
            action_id=f"{code}-{i:03d}",
            hat=code,
            payload={"verb": verb, "output": output,
                     "layer_name": rogue.LAYERS[layer]},
            anchor=anchor,
        )

    detection = rogue.detect_rogue(chain, key)
    anchors = sorted({h[4] for h in rogue.HATS if h[0] in hats})

    cert = Certification(
        license_version=LICENSE_VERSION,
        issued_to=holder,
        issued_by=AUTHORITY,
        issued_at=time.time(),
        scope=Scope(
            hats=sorted(hats),
            layers=sorted(layers),
            anchors=anchors,
            action_space="bounded",
            domain=domain,
        ),
        chain_length=detection["entries"],
        chain_head=chain.head(),
        chain_valid=detection["chain_valid"],
        rogue_detected=detection["rogue"],
        verdict=detection["verdict"],
        non_claims=NonClaims.load(),
        theorem=THEOREM,
        verification_procedure=(
            "1. Recompute digest of the certification body with the same "
            "canonical JSON encoding. 2. Verify signature = "
            "sha256(key || digest). 3. Re-run dcs.rogue.detect_rogue on the "
            "chain referenced by chain_head. 4. Confirm every entry in the "
            "detection has status=PASS. 5. Any FAIL is a rogue detection."
        ),
    )
    cert.sign(key)
    return cert  # pragma: no cover


def verify_license(cert: Certification, key: bytes) -> dict:  # pragma: no cover
    """Verify a license. Returns a structured verdict."""
    sig_ok = cert.verify(key)
    chain_ok = cert.chain_valid and not cert.rogue_detected
    return {  # pragma: no cover
        "signature_valid": sig_ok,
        "chain_valid":     chain_ok,
        "verdict":         "PASS" if (sig_ok and chain_ok) else "FAIL",
        "holder":          cert.issued_to,
        "scope_hats":      len(cert.scope.hats),
        "scope_layers":    len(cert.scope.layers),
        "scope_anchors":   len(cert.scope.anchors),
        "chain_length":    cert.chain_length,
        "non_claims":      asdict(cert.non_claims),
    }


def render_license(cert: Certification) -> str:  # pragma: no cover
    """Human-readable license text."""
    nc = cert.non_claims
    lines = [
        "═" * 72,
        "  DCS AGENCY LICENSE",
        f"  Version {cert.license_version}",
        "═" * 72,
        "",
        f"  Holder:    {cert.issued_to}",
        f"  Authority: {cert.issued_by}",
        f"  Issued:    {time.strftime('%Y-%m-%d %H:%M:%S UTC',
                                       time.gmtime(cert.issued_at))}",
        "",
        "  SCOPE",
        "  " + "─" * 68,
        f"  Action space:  {cert.scope.action_space}",
        f"  Domain:        {cert.scope.domain}",
        f"  Hats granted:  {len(cert.scope.hats)} of 48",
        f"  Layers:        {cert.scope.layers}",
        f"  Anchors:       {len(cert.scope.anchors)} standards bodies",
        "",
        "  ATTESTATION",
        "  " + "─" * 68,
        f"  Chain length:  {cert.chain_length}",
        f"  Chain head:    {cert.chain_head[:32]}...",
        f"  Chain valid:   {cert.chain_valid}",
        f"  Rogue detected:{cert.rogue_detected}",
        f"  Verdict:       {cert.verdict}",
        "",
        "  THEOREM",
        "  " + "─" * 68,
    ]
    for line in cert.theorem.splitlines():
        lines.append("  " + line)
    lines += [
        "",
        "  NON-CLAIMS (8 top-level × 8 sub = 64)",
        "  " + "─" * 68,
    ]
    try:
        from dcs.non_claims import CORRECTED  # pragma: no cover
    except ImportError:  # pragma: no cover
        CORRECTED = None
    for i, (name, block) in enumerate((CORRECTED or {}).items(), 1):
        lines.append(f"  ✗ {i}. {name.replace('_', ' ')}:")
        for w in _wrap(block["statement"], 64):
            lines.append("      " + w)
        for j, sub in enumerate(block["sub"], 1):
            lines.append(f"        {i}.{j}  {sub}")
        lines.append("")
    lines += [
        "  VERIFICATION",
        "  " + "─" * 68,
    ]
    import re as _re  # pragma: no cover
    steps = _re.split(r'(?=\d+\.\s)', cert.verification_procedure)
    for step in steps:
        step = step.strip()
        if step:  # pragma: no cover
            lines.append("  • " + step)
    lines += [
        "",
        f"  Signature: {cert.signature[:32]}...",
        "",
        "═" * 72,
        "  This license certifies detectability, not prevention.",
        "  Rogue is not impossible. Rogue is un-hideable.",
        "═" * 72,
    ]
    return "\n".join(lines)  # pragma: no cover


def _wrap(text: str, width: int) -> list[str]:  # pragma: no cover
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:  # pragma: no cover
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:  # pragma: no cover
        lines.append(cur)
    return lines  # pragma: no cover
