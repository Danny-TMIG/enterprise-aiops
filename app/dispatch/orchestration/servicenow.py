from __future__ import annotations

import os

from app.dispatch.orchestration.base import (
    OrchestratorBackend,
    VerificationClaim,
    VerificationVerdict,
)


class ServiceNowBackend(OrchestratorBackend):
    """Plugs into Now Assist / Flow Designer as a REST step."""
    name = "servicenow"

    def available(self) -> bool:
        return bool(os.environ.get("SERVICENOW_INSTANCE"))

    def _verify(self, claim: VerificationClaim) -> VerificationVerdict:
        from app.dispatch.verification.registry import VerificationRegistry
        out = VerificationRegistry().verify_all(claim.claim, claim.evidence)
        ok = all(v.status == "PASS" for v in out)
        return VerificationVerdict(
            vendor=self.name,
            status="PASS" if ok else "FAIL",
            rationale="now-assist verify",
            evidence_used=[e.get("id", "?") for e in claim.evidence],
            dry_run=not self.available(),
        )
