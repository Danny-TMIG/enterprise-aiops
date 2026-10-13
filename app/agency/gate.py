"""The gate: can a subject act on a capability, right now?

Returns one of the RESULT STATES from the atlas:

    PASS
    NOT_AUTHORIZED   — no live Agency for this scope
    POLICY_DENIED    — no live License for this domain/jurisdiction
    QUALIFICATION_DENIED — required Certification missing or revoked
    INSUFFICIENT_EVIDENCE — required Expertise below threshold
    EXPIRED          — a required record has expired

The gate never consults an LLM. It consults the registry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agency.registry import Registry, get_registry


@dataclass
class Decision:
    state: str
    subject: str
    capability: str
    reason: str = ""
    evidence: list[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "subject": self.subject,
            "capability": self.capability,
            "reason": self.reason,
            "evidence": self.evidence or [],
        }


def _live(records, scope_attr: str, scope_val: str):
    return [r for r in records if r.live and getattr(r, scope_attr, None) == scope_val]


def gate(
    subject: str,
    capability: str,
    *,
    scope: str,
    domain: str,
    jurisdiction: str,
    required_standard: str | None = None,
    required_level: str | None = None,
    min_expertise: float = 0.0,
    registry: Registry | None = None,
) -> Decision:
    reg = registry or get_registry()
    everything = reg.for_subject(subject)

    # 1. Agency
    agencies = _live(everything["agency"], "scope", scope)
    if not agencies:
        any_scope = [r.scope for r in everything["agency"] if r.live]
        if any_scope:
            return Decision("NOT_AUTHORIZED", subject, capability,
                            f"agency exists but not for scope '{scope}'; "
                            f"held scopes: {any_scope}")
        return Decision("NOT_AUTHORIZED", subject, capability,
                        f"no live agency for scope '{scope}'")

    # 2. License
    licenses = [r for r in everything["license"]
                if r.live and r.domain == domain and r.jurisdiction == jurisdiction]
    if not licenses:
        return Decision("POLICY_DENIED", subject, capability,
                        f"no live license for '{domain}' under '{jurisdiction}'")

    # 3. Certification (optional unless required)
    if required_standard:
        ok_certs = [r for r in everything["cert"]
                    if r.live
                    and r.standard == required_standard
                    and (required_level is None or r.level == required_level)]
        if not ok_certs:
            return Decision("QUALIFICATION_DENIED", subject, capability,
                            f"missing live cert {required_standard}"
                            + (f" {required_level}" if required_level else ""))

    # 4. Expertise (earned)
    exps = [r for r in everything["expertise"] if r.domain == domain]
    if min_expertise > 0.0:
        if not exps:
            return Decision("INSUFFICIENT_EVIDENCE", subject, capability,
                            f"no expertise history in '{domain}'")
        best = max(e.score() for e in exps)
        if best < min_expertise:
            return Decision("INSUFFICIENT_EVIDENCE", subject, capability,
                            f"expertise {best} < required {min_expertise}")

    evidence = []
    evidence += [a.evidence_hash for a in agencies]
    evidence += [l.evidence_hash for l in licenses]
    if exps:
        evidence += exps[0].evidence_hashes[-4:]

    return Decision("PASS", subject, capability,
                    "all gates cleared", evidence=evidence)


class GateEvaluator:

    """Stateful wrapper around the module-level gate().

    `evaluate(context)` resolves subject+capability from the context
    (or uses the context dict directly as a registry lookup key), calls
    gate() against the real registry, and returns the Decision dict.
    """
    def __init__(self, registry: Registry | None = None):
        self.registry = registry or get_registry()

    def evaluate(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        ctx = dict(context or {})
        subj = ctx.get("subject")
        cap = ctx.get("capability")
        if not (subj and cap):
            # Nothing to gate: return the observation unchanged.
            return {"state": "PASS", "context": ctx}
        try:
            decision = gate(
                subj, cap,
                scope=ctx.get("scope", "default"),
                domain=ctx.get("domain", "default"),
                jurisdiction=ctx.get("jurisdiction", "default"),
                required_standard=ctx.get("required_standard"),
                min_expertise=float(ctx.get("min_expertise", 0.0)),
                registry=self.registry,
            )
            return decision.to_dict()
        except Exception as exc:
            return {"state": "ERROR", "reason": f"{type(exc).__name__}: {exc}",
                    "subject": subj, "capability": cap}

