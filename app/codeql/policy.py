"""Policy gate over CodeQL reports.

    fail_on_severity: any finding at or above this level fails.
    max_findings:     total findings must be <= this.
    allow_rules:      rules always allowed (exempt).
    deny_rules:       rules always denied (fail fast).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.codeql.report import Report

_SEVERITY_ORDER = {"none": 0, "note": 1, "warning": 2, "error": 3}


@dataclass
class Policy:
    fail_on_severity: str = "error"
    max_findings: int = 0
    allow_rules: set[str] = field(default_factory=set)
    deny_rules: set[str] = field(default_factory=set)


@dataclass
class PolicyDecision:
    ok: bool
    reason: str
    offending: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"ok": self.ok, "reason": self.reason,
                "offending": list(self.offending)}


def load_policy(doc: dict | None = None) -> Policy:
    doc = doc or {}
    return Policy(
        fail_on_severity=doc.get("fail_on_severity", "error"),
        max_findings=int(doc.get("max_findings", 0)),
        allow_rules=set(doc.get("allow_rules", []) or []),
        deny_rules=set(doc.get("deny_rules", []) or []),
    )


def apply_policy(report: Report, policy: Policy) -> PolicyDecision:
    threshold = _SEVERITY_ORDER.get(policy.fail_on_severity, 3)
    offending: list[str] = []

    for f in report.findings:
        if f.rule_id in policy.deny_rules:
            offending.append(f"{f.rule_id} @ {f.file}:{f.line} (denied)")
            continue
        if f.rule_id in policy.allow_rules:
            continue
        sev = _SEVERITY_ORDER.get(f.severity, 2)
        if sev >= threshold:
            offending.append(f"{f.rule_id} @ {f.file}:{f.line} ({f.severity})")

    if offending:
        return PolicyDecision(ok=False,
                              reason=f"{len(offending)} finding(s) breach policy",
                              offending=offending[:50])

    if report.total > policy.max_findings:
        return PolicyDecision(
            ok=False,
            reason=f"total {report.total} > max {policy.max_findings}",
        )

    return PolicyDecision(ok=True, reason="policy satisfied")
