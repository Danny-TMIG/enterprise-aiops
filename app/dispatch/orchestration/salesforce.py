from __future__ import annotations

import os

from app.dispatch.orchestration.base import (
    OrchestratorBackend,
    VerificationClaim,
    VerificationVerdict,
)


class SalesforceBackend(OrchestratorBackend):
    """Plugs into Agentforce as an External Service / Apex callout."""
    name = "salesforce"

    def available(self) -> bool:
        return bool(os.environ.get("SALESFORCE_ORG_URL"))

    def _verify(self, claim: VerificationClaim) -> VerificationVerdict:
        from app.dispatch.verification.registry import VerificationRegistry
        out = VerificationRegistry().verify_all(claim.claim, claim.evidence)
        ok = all(v.status == "PASS" for v in out)
        return VerificationVerdict(
            vendor=self.name,
            status="PASS" if ok else "FAIL",
            rationale="agentforce verify",
            evidence_used=[e.get("id", "?") for e in claim.evidence],
            dry_run=not self.available(),
        )
