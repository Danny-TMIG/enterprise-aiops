"""Universal bootstrap manager for dispatchpatch subpackages and registries."""

from app.dispatchpatch.evidence.aar import AAREvidence
from app.dispatchpatch.evidence.novafabric import NovaFabricEvidence
from app.dispatchpatch.evidence.registry import EvidenceRegistry
from app.dispatchpatch.models.local_mlx import LocalMLXModel
from app.dispatchpatch.models.registry import ModelRegistry
from app.dispatchpatch.orchestration.google import GoogleOrchestrator
from app.dispatchpatch.orchestration.microsoft import MicrosoftOrchestrator
from app.dispatchpatch.orchestration.registry import OrchestratorRegistry
from app.dispatchpatch.orchestration.salesforce import SalesforceOrchestrator
from app.dispatchpatch.orchestration.servicenow import ServiceNowOrchestrator
from app.dispatchpatch.protocols.a2a import A2AProtocol
from app.dispatchpatch.protocols.mcp import MCPProtocol
from app.dispatchpatch.runtime import run_dispatch_patch
from app.dispatchpatch.scan.codacy import CodacyScan
from app.dispatchpatch.scan.codeql import CodeQLScan
from app.dispatchpatch.scan.registry import ScanRegistry
from app.dispatchpatch.verification.kernel import KernelVerification
from app.dispatchpatch.verification.lean4agent import Lean4AgentVerification
from app.dispatchpatch.verification.leandojo import LeanDojoVerification
from app.dispatchpatch.verification.prove2me import Prove2MeVerification
from app.dispatchpatch.verification.registry import VerificationRegistry


class DispatchPatchBootstrap:
    _initialized = False

    @classmethod
    def initialize(cls):
        """Registers all concrete implementations into their respective registries."""
        if cls._initialized:
            return

        EvidenceRegistry.register("aar", AAREvidence)
        EvidenceRegistry.register("novafabric", NovaFabricEvidence)

        ModelRegistry.register("local_mlx", LocalMLXModel)

        OrchestratorRegistry.register("google", GoogleOrchestrator)
        OrchestratorRegistry.register("microsoft", MicrosoftOrchestrator)
        OrchestratorRegistry.register("salesforce", SalesforceOrchestrator)
        OrchestratorRegistry.register("servicenow", ServiceNowOrchestrator)

        ScanRegistry.register("codacy", CodacyScan)
        ScanRegistry.register("codeql", CodeQLScan)

        VerificationRegistry.register("kernel", KernelVerification)
        VerificationRegistry.register("lean4agent", Lean4AgentVerification)
        VerificationRegistry.register("leandojo", LeanDojoVerification)
        VerificationRegistry.register("prove2me", Prove2MeVerification)

        cls._initialized = True

    @staticmethod
    def execute_pipeline(
        target: str,
        orchestrator_name: str = "google",
        model_name: str = "local_mlx",
        scan_name: str = "codeql",
        verifier_name: str = "kernel",
        evidence_type: str = "aar",
        evidence_payload: dict | None = None,
        protocol: str = "mcp",
        prompt: str = "Execute verification and sync",
        proof: str = "proven kernel validation",
        code: str = "# sample code"
    ) -> dict:
        DispatchPatchBootstrap.initialize()

        runtime_res = run_dispatch_patch(target)

        ev_cls = EvidenceRegistry.get(evidence_type)
        evidence = ev_cls(evidence_payload or {evidence_type: True})
        is_valid_evidence = evidence.validate()

        model_cls = ModelRegistry.get(model_name)
        model = model_cls(model_name)
        model_output = model.generate(prompt)

        orch_cls = OrchestratorRegistry.get(orchestrator_name)
        orchestrator = orch_cls()
        orch_output = orchestrator.orchestrate(target)

        scan_cls = ScanRegistry.get(scan_name)
        scanner = scan_cls()
        scan_result = scanner.scan(code)

        ver_cls = VerificationRegistry.get(verifier_name)
        verifier = ver_cls()
        verification_result = verifier.verify(proof)

        proto_handler = MCPProtocol() if protocol == "mcp" else A2AProtocol()
        proto_output = proto_handler.handle(target)

        return {
            "runtime": runtime_res,
            "evidence_valid": is_valid_evidence,
            "model_output": model_output,
            "orchestration": orch_output,
            "scan_result": scan_result,
            "verification_valid": verification_result,
            "protocol_output": proto_output,
        }


def get_bootstrap_manager() -> type[DispatchPatchBootstrap]:
    DispatchPatchBootstrap.initialize()
    return DispatchPatchBootstrap
