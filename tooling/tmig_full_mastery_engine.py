#!/usr/bin/env python3
"""
THE MARK INTELLIGENCE GROUP (TMIG)
FULL MONOREPO MASTERY & 75-COMPONENT TAXONOMY ENFORCER (ASF v1.2)
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Complete 75-Component Register mapped to AX, AG, AC layers
COMPONENTS = {
    "components/ax": [
        "COG-INT-001-experience-surface",
        "COG-INT-002-session-and-workspace-runtime",
        "COG-INT-003-human-control-layer",
        "COG-CORE-001-cognitive-runtime",
        "COG-CORE-002-cognitive-state-manager",
        "COG-CORE-003-memory-fabric",
        "COG-CORE-004-semantic-representation-layer",
        "COG-REA-001-knowledge-interface",
        "COG-REA-002-cognitive-router",
        "COG-REA-003-reasoning-fabric",
        "COG-REA-004-planning-and-decomposition",
        "COG-REA-005-evaluator-and-critic",
        "COG-CMP-001-model-and-substrate-adapter",
        "COG-CMP-002-skill-and-capability-interface",
        "COG-CMP-003-cognitive-cell-runtime",
        "COG-CMP-004-swarm-coordinator",
        "COG-CMP-005-adaptation-manager",
        "COG-ASSUR-001-evidence-projection",
        "COG-ASSUR-002-replay-and-evaluation-runtime",
        "COG-ASSUR-003-performance-manager",
        "COG-ASSUR-004-security-integration",
    ],
    "components/ag": [
        "GOV-KRN-001-governance-object-model-and-registry",
        "GOV-KRN-002-governed-state-and-transition-engine",
        "GOV-KRN-003-decision-and-outcome-correlation",
        "GOV-IAM-001-principal-and-domain-identity-registry",
        "GOV-IAM-002-authority-delegation-consent-and-revocation",
        "GOV-IAM-003-authorization-decision-engine",
        "GOV-IAM-004-human-approval-and-escalation",
        "GOV-POL-001-policy-registry-and-integrity",
        "GOV-POL-002-policy-decision-engine",
        "GOV-POL-003-policy-lifecycle-amendment-and-distribution",
        "GOV-INF-001-classification-and-labeling",
        "GOV-INF-002-information-flow-decision-engine",
        "GOV-INF-003-liquid-aperture-release-control",
        "GOV-INF-004-schema-and-data-contract-registry",
        "GOV-INF-005-ingestion-governance-and-lineage-coordinator",
        "GOV-CAP-001-capability-registry",
        "GOV-CAP-002-capability-authorization-and-eligibility",
        "GOV-CAP-003-governed-action-and-execution-order-coordinator",
        "GOV-EVD-001-decision-and-cross-component-evidence-correlation",
        "GOV-EVD-002-governed-outcome-verification-and-audit-reconstruction",
        "GOV-EVD-003-attestation-verification-and-artifact-assurance",
        "GOV-ADM-001-govern-control-plane-and-configuration",
        "GOV-ADM-002-health-observability-security-and-incident-interface",
        "GOV-FED-001-federation-gateway-and-domain-exchange-coordinator",
    ],
    "components/ac": [
        "CMP-CTL-001-compute-contract-kernel",
        "CMP-CTL-002-execution-gateway",
        "CMP-CTL-003-control-plane-coordinator",
        "CMP-CTL-004-node-agent",
        "CMP-TRU-001-hardware-identity",
        "CMP-TRU-002-attestation-gateway",
        "CMP-TRU-003-trust-evaluation",
        "CMP-TRU-004-secure-execution-environment",
        "CMP-TRU-005-artifact-integrity-and-supply-chain",
        "CMP-TRU-006-secrets-and-key-delivery",
        "CMP-RES-001-topology-model",
        "CMP-RES-002-topology-resolver",
        "CMP-RES-003-resource-model-and-inventory",
        "CMP-RES-004-resource-discovery-and-advertisement",
        "CMP-RES-005-resource-resolver",
        "CMP-RES-006-allocation-and-reservation",
        "CMP-RES-007-admission-quota-and-lease-manager",
        "CMP-EXE-001-workload-package-manager",
        "CMP-EXE-002-native-runtime",
        "CMP-EXE-003-runtime-adapter-manager",
        "CMP-EXE-004-scheduler",
        "CMP-EXE-005-runtime-lifecycle-manager",
        "CMP-EXE-006-checkpoint-and-migration-manager",
        "CMP-EXE-007-recovery-coordinator",
        "CMP-DAT-001-data-staging-and-result-collection",
        "CMP-DAT-002-network-and-data-movement-controller",
        "CMP-EVD-001-observation-and-telemetry",
        "CMP-EVD-002-evidence-bridge",
        "CMP-EVD-003-physical-provenance",
        "CMP-ECO-001-quote-and-economic-optimizer",
    ],
}

ROOT_DIRS = [
    "catalog",
    "contracts",
    "libraries",
    "deploy/profiles/departmental-cpu",
    "deploy/profiles/enterprise-multidepartment",
    "deploy/profiles/device-continuity",
    "deploy/releases/release-v1.0.0",
    "integration",
    "docs/runbooks",
    "tooling",
    "examples",
    ".github",
]


def bootstrap_tmig_monorepo():
    print("🛡️ [TMIG] Initializing full ASF v1.2 monorepo structure for 75 components[cite: 2]...")

    # 1. Create root directories
    for d in ROOT_DIRS:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

    total_components = 0

    # 2. Populate component sub-trees
    for base_path, comp_list in COMPONENTS.items():
        for comp in comp_list:
            comp_dir = ROOT / base_path / comp
            (comp_dir / "src" / "public").mkdir(parents=True, exist_ok=True)
            (comp_dir / "src" / "modules").mkdir(parents=True, exist_ok=True)
            (comp_dir / "src" / "adapters").mkdir(parents=True, exist_ok=True)
            (comp_dir / "tests" / "unit").mkdir(parents=True, exist_ok=True)
            (comp_dir / "tests" / "contract").mkdir(parents=True, exist_ok=True)
            (comp_dir / "tests" / "component").mkdir(parents=True, exist_ok=True)
            (comp_dir / "tests" / "fixtures").mkdir(parents=True, exist_ok=True)
            (comp_dir / "config").mkdir(parents=True, exist_ok=True)
            (comp_dir / "migrations").mkdir(parents=True, exist_ok=True)
            (comp_dir / "docs").mkdir(parents=True, exist_ok=True)

            # Write required markdown files per section 4
            (comp_dir / "README.md").write_text(
                f"# Component: {comp}\nGoverned by ASF v1.2 specification[cite: 2]."
            )
            (comp_dir / "CHANGELOG.md").write_text(
                f"# Changelog - {comp}\n- Initial release candidate under ASF v1.2[cite: 2]."
            )
            (comp_dir / "component.json").write_text(
                json.dumps(
                    {"component_id": comp, "status": "active", "compliance": "ASF v1.2"}, indent=2
                )
            )

            total_components += 1

    # 3. Generate catalog inventory JSON
    catalog_data = {
        "organization": "The Mark Intelligence Group",
        "standard": "ASF v1.2",
        "total_components": total_components,
        "layers": {
            "AX_Cognition": len(COMPONENTS["components/ax"]),
            "AG_Govern": len(COMPONENTS["components/ag"]),
            "AC_Compute": len(COMPONENTS["components/ac"]),
        },
    }

    catalog_file = ROOT / "catalog" / "components.json"
    catalog_file.write_text(json.dumps(catalog_data, indent=2))

    # 4. Generate Omega Cryptographic Seal
    payload = json.dumps(catalog_data, sort_keys=True).encode("utf-8")
    omega_seal = hashlib.sha256(payload).hexdigest()

    seal_file = ROOT / "deploy" / "ledgers" / "tmig_master_seal.json"
    seal_file.parent.mkdir(parents=True, exist_ok=True)
    seal_file.write_text(json.dumps({"catalog": catalog_data, "omega_seal": omega_seal}, indent=2))

    print(
        f"💯 [SUCCESS] Provisioned all {total_components} component packages across AX, AG, and AC[cite: 2]."
    )
    print(f"🔒 [SEAL] TMIG Master Omega Seal: {omega_seal}")


if __name__ == "__main__":
    bootstrap_tmig_monorepo()
