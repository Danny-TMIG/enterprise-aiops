from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class VerificationClaim:
    claim: str
    subject: str = ""
    evidence: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationVerdict:
    vendor: str
    status: str           # PASS | FAIL | UNKNOWN | NOT_RUN | ...
    rationale: str = ""
    evidence_used: list[str] = field(default_factory=list)
    dry_run: bool = False
    ts: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vendor": self.vendor, "status": self.status,
            "rationale": self.rationale,
            "evidence_used": self.evidence_used,
            "dry_run": self.dry_run, "ts": self.ts,
        }


class OrchestratorBackend:
    """Vendor-agnostic orchestrator surface.

    An orchestrator (Microsoft/Salesforce/ServiceNow/Google) calls the
    mesh as a *verification backend*: it sends a claim + evidence, the
    mesh returns a verdict. The mesh never calls the orchestrator's
    model — it only consumes its verification traffic.
    """

    name: str = "orchestrator"

    def available(self) -> bool:
        return True

    def verify(self, claim: VerificationClaim) -> VerificationVerdict:
        try:
            return self._verify(claim)
        except Exception as exc:  # noqa: BLE001
            return VerificationVerdict(
                vendor=self.name, status="UNKNOWN",
                rationale=f"backend error: {type(exc).__name__}",
                dry_run=True,
            )

    def _verify(self, claim: VerificationClaim) -> VerificationVerdict:
        # Default: caller supplied evidence already; run local checks
        from app.dispatch.verification.registry import VerificationRegistry
        reg = VerificationRegistry()
        out = reg.verify_all(claim.claim, claim.evidence)
        ok = all(v.status == "PASS" for v in out)
        return VerificationVerdict(
            vendor=self.name,
            status="PASS" if ok else "FAIL",
            rationale="local verifiers: " + ", ".join(
                f"{v.prover}={v.status}" for v in out),
            evidence_used=[e.get("id", "?") for e in claim.evidence],
        )
