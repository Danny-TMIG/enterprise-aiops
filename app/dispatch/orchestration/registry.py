from __future__ import annotations

from typing import Any

from app.dispatch.orchestration.base import (
    OrchestratorBackend,
    VerificationClaim,
    VerificationVerdict,
)
from app.dispatch.orchestration.google import GoogleBackend
from app.dispatch.orchestration.microsoft import MicrosoftBackend
from app.dispatch.orchestration.salesforce import SalesforceBackend
from app.dispatch.orchestration.servicenow import ServiceNowBackend


class OrchestrationRegistry:
    def __init__(self) -> None:
        self.backends: dict[str, OrchestratorBackend] = {
            "microsoft":  MicrosoftBackend(),
            "salesforce": SalesforceBackend(),
            "servicenow": ServiceNowBackend(),
            "google":     GoogleBackend(),
        }

    def list(self) -> dict[str, Any]:
        return {n: {"available": b.available()}
                for n, b in self.backends.items()}

    def verify(self, vendor: str,
               claim: VerificationClaim) -> VerificationVerdict:
        b = self.backends.get(vendor)
        if not b:
            return VerificationVerdict(vendor=vendor, status="UNSUPPORTED",
                                       rationale="unknown vendor")
        return b.verify(claim)
