from __future__ import annotations
from typing import Any, Dict, List

from app.dispatch.orchestration.base import (
    OrchestratorBackend, VerificationClaim, VerificationVerdict,
)
from app.dispatch.orchestration.microsoft import MicrosoftBackend
from app.dispatch.orchestration.salesforce import SalesforceBackend
from app.dispatch.orchestration.servicenow import ServiceNowBackend
from app.dispatch.orchestration.google import GoogleBackend


class OrchestrationRegistry:
    def __init__(self) -> None:
        self.backends: Dict[str, OrchestratorBackend] = {
            "microsoft":  MicrosoftBackend(),
            "salesforce": SalesforceBackend(),
            "servicenow": ServiceNowBackend(),
            "google":     GoogleBackend(),
        }

    def list(self) -> Dict[str, Any]:
        return {n: {"available": b.available()}
                for n, b in self.backends.items()}

    def verify(self, vendor: str,
               claim: VerificationClaim) -> VerificationVerdict:
        b = self.backends.get(vendor)
        if not b:
            return VerificationVerdict(vendor=vendor, status="UNSUPPORTED",
                                       rationale="unknown vendor")
        return b.verify(claim)
