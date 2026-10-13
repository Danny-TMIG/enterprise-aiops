from __future__ import annotations

import os

from app.dispatch.orchestration.base import (
    OrchestratorBackend,
    VerificationClaim,
    VerificationVerdict,
)


class MicrosoftBackend(OrchestratorBackend):
    """Plugs into Copilot Studio / Power Platform as a custom connector."""
    name = "microsoft"

    def available(self) -> bool:
        return bool(os.environ.get("MICROSOFT_VERIFY_ENDPOINT"))

    def _verify(self, claim: VerificationClaim) -> VerificationVerdict:
        # Real integrations POST to Power Automate; here we run local
        # verification and shape the verdict for the connector response.
        from app.dispatch.verification.registry import VerificationRegistry
        out = VerificationRegistry().verify_all(claim.claim, claim.evidence)
        ok = all(v.status == "PASS" for v in out)
        return VerificationVerdict(
            vendor=self.name,
            status="PASS" if ok else "FAIL",
            rationale="power-platform verify",
            evidence_used=[e.get("id", "?") for e in claim.evidence],
            dry_run=not self.available(),
        )
