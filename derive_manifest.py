#!/usr/bin/env python3
"""derive_manifest.py — derive catalog/spec_manifest.json from the three FAS docs.

Fields populated only from what the documents state:
  id, layer, group, title, owned_result, release, invariants (layer-level),
  boundary_contracts (layer-level), open_decisions (gating IDs).

Anything the documents do not state is set to "UNDECIDED" with a
governing decision id where one is named. Nothing is invented.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "catalog" / "spec_manifest.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

# Layer-level invariants, quoted from the documents.
COG_INVARIANTS = [
    "No model is Cognition; models and solvers are replaceable cognitive substrates.",
    "Persistent cognitive state and memory are distinct from prompts, context windows, caches, weights, recurrent state, and execution state.",
    "Memory is typed and provenance-bearing; memory is not automatically truth.",
    "Reasoning is compositional and may combine neural, symbolic, numerical, search, proof, simulation, retrieval, or hybrid methods.",
    "Proposal remains distinct from authorization, and execution remains distinct from semantic verification.",
    "Failures, uncertainty, contradiction, denial, abstention, degradation, and incomplete evidence remain visible.",
    "Optimization cannot silently change governed semantics, disclosure, eligibility, or assurance.",
    "Human control is authenticated through Govern; generated content cannot create authority.",
    "Research mechanisms remain nonnormative until their mathematics, validation, and adoption gates are met.",
]

GOV_INVARIANTS = [
    "GOV-INV-001 Cognition cannot authorize its own consequential action.",
    "GOV-INV-002 Govern cannot execute a physical workload or represent scheduling as authority.",
    "GOV-INV-003 Compute cannot broaden an execution order, select an unauthorized capability, or reinterpret policy.",
    "GOV-INV-004 Authority, delegation, consent, and approval are bounded, attributable, time-aware, and revocable.",
    "GOV-INV-005 Information movement and release require an explicit decision; transformation cannot increase authority.",
    "GOV-INV-006 Mandatory constraints determine eligibility before optimization or convenience.",
    "GOV-INV-007 Every consequential terminal outcome has an immutable, reconstructible evidence chain.",
    "GOV-INV-008 Missing identity, authority, policy, classification, integrity, or evidence dependencies fail closed.",
    "GOV-INV-009 Historical state and policy are corrected by supersession, not silent mutation.",
    "GOV-INV-010 Unvalidated mathematics or research mechanisms are never represented as implemented guarantees.",
]

CMP_INVARIANTS = [
    "CMP-INV-001 Aether Compute executes only a valid, current, attributable order issued through Aether Govern.",
    "CMP-INV-002 Compute cannot broaden authority, relax policy, alter information-flow permission, or substitute a capability outside the governed set.",
    "CMP-INV-003 Mandatory authorization, policy, flow, capability, trust, attestation, topology, artifact, and resource conditions are conjunctive.",
    "CMP-INV-004 Economic optimization and preference ranking operate only within the eligible set.",
    "CMP-INV-005 Every executing workload is bound to one order, workload identity, package version, reservation, node identity, and evidence context.",
    "CMP-INV-006 No node or workload participates after its required identity, attestation, trust, lease, artifact, or order validity expires.",
    "CMP-INV-007 Cancellation and revocation dominate new dispatch and trigger explicit in-flight handling.",
    "CMP-INV-008 Retries, recovery, migration, and projection changes cannot duplicate non-idempotent effects or erase causal history.",
    "CMP-INV-009 Protected inputs, outputs, secrets, network flows, and checkpoints remain within their authorized classification, purpose, residency, and retention envelope.",
    "CMP-INV-010 Every terminal execution state has sufficient typed evidence to show what was attempted, where, with what artifacts, and with which assurance limits.",
    "CMP-INV-011 Missing or contradictory mandatory evidence prevents a verified-complete claim.",
    "CMP-INV-012 Unvalidated topology, trust, arity, security, ledger, quantum, or economic mechanisms are never represented as production guarantees.",
]

COG_BOUNDARY = {
    "knowledge": "KnowledgeQuery remains internal; cross-layer access uses KnowledgeAccessRequest and returns GovernedKnowledgeResult.",
    "capabilities": "CapabilityRequest projects to Govern and returns GovernedCapabilitySet; Cognition cannot self-authorize capability use.",
    "human_control": "Govern produces ApprovalRequest; Cognition presents HumanControlPresentation and returns HumanDecisionSubmission.",
    "outcome": "Cognition consumes GovernedOutcome and applies only an authorized CognitiveStateUpdateDirective.",
    "control": "CancellationRevocationDirective and ASFError are mandatory cross-layer control objects.",
}

GOV_BOUNDARY = {
    "authority": "AuthorizationRequest and AuthorizationDecision are the sole cross-layer authority-decision contracts.",
    "information": "InformationFlowRequest and InformationFlowDecision govern disclosure; GovernedKnowledgeResult carries the released representation.",
    "capabilities": "CapabilityRequest is resolved to GovernedCapabilitySet under authority and policy.",
    "execution": "ExecutionOrder is the sole Govern-to-Compute boundary command; Govern consumes ExecutionStatus, ExecutionResult, and ExecutionEvidence.",
    "closure": "Govern emits GovernedOutcome and CognitiveStateUpdateDirective only after evidence reconciliation.",
    "control": "Approval, cancellation, revocation, common envelope, and ASFError contracts apply consistently across boundaries.",
}

CMP_BOUNDARY = {
    "command": "Aether Compute receives ExecutionOrder. ExecutionRequest is an internal normalized projection.",
    "return": "ExecutionStatus, ExecutionResult, and ExecutionEvidence are returned to Govern with correlation and integrity context.",
    "envelope": "All cross-layer objects use the ASF Common Envelope.",
    "control": "CancellationRevocationDirective must interrupt admission, placement, execution, recovery, and result publication.",
    "failure": "ASFError is the cross-layer error contract.",
}

BOUNDARY_INVARIANTS = [
    "Every boundary object carries schema version, correlation, causation, sovereign-domain, purpose, classification, integrity, and evidence context.",
    "Every retry uses a stable idempotency key; duplicate delivery may not duplicate authority, state mutation, execution, or evidence commitment.",
    "Expired, revoked, malformed, unsupported, unsigned, or context-inconsistent objects fail closed for consequential action.",
    "Cancellation and revocation remain observable state transitions and cannot be represented as ordinary execution failure.",
    "The producer owns semantic validity at emission; the consumer independently validates before acting.",
]

# Component inventory, transcribed from the three Appendix A / component tables.
COG = {
    "COG-INT-001": ("Interaction and Human Control", "Experience Surface", "Core v1"),
    "COG-INT-002": ("Interaction and Human Control", "Session and Workspace Runtime", "Core v1"),
    "COG-INT-003": ("Interaction and Human Control", "Human Control Layer", "Core v1"),
    "COG-CORE-001": ("Cognitive Runtime, State and Memory", "Cognitive Runtime", "Core v1"),
    "COG-CORE-002": ("Cognitive Runtime, State and Memory", "Cognitive State Manager", "Core v1"),
    "COG-CORE-003": ("Cognitive Runtime, State and Memory", "Memory Fabric", "Core v1"),
    "COG-CORE-004": ("Knowledge, Reasoning and Planning", "Semantic Representation Layer", "Core v1"),
    "COG-REA-001": ("Knowledge, Reasoning and Planning", "Knowledge Interface", "Core v1"),
    "COG-REA-002": ("Knowledge, Reasoning and Planning", "Cognitive Router", "Core v1"),
    "COG-REA-003": ("Knowledge, Reasoning and Planning", "Reasoning Fabric", "Core v1"),
    "COG-REA-004": ("Knowledge, Reasoning and Planning", "Planning and Decomposition", "Core v1"),
    "COG-REA-005": ("Knowledge, Reasoning and Planning", "Evaluator and Critic", "Core v1"),
    "COG-CMP-001": ("Models, Skills and Cognitive Composition", "Model and Substrate Adapter", "Core v1"),
    "COG-CMP-002": ("Models, Skills and Cognitive Composition", "Skill and Capability Interface", "Core v1"),
    "COG-CMP-003": ("Models, Skills and Cognitive Composition", "Cognitive Cell Runtime", "Core v1"),
    "COG-CMP-004": ("Models, Skills and Cognitive Composition", "Swarm Coordinator", "Research-gated / deferred"),
    "COG-CMP-005": ("Models, Skills and Cognitive Composition", "Adaptation Manager", "Core v1"),
    "COG-ASSUR-001": ("Assurance, Security and Performance", "Evidence Projection", "Core v1"),
    "COG-ASSUR-002": ("Assurance, Security and Performance", "Replay and Evaluation Runtime", "Core v1"),
    "COG-ASSUR-003": ("Assurance, Security and Performance", "Performance Manager", "Core v1"),
    "COG-ASSUR-004": ("Assurance, Security and Performance", "Security Integration", "Core v1"),
}

GOV = {
    "GOV-KRN-001": ("Governance Kernel", "Governance Object Model and Registry", "Core v1"),
    "GOV-KRN-002": ("Governance Kernel", "Governed State and Transition Engine", "Core v1"),
    "GOV-KRN-003": ("Governance Kernel", "Decision and Outcome Correlation", "Core v1"),
    "GOV-IAM-001": ("Identity and Authority", "Principal and Domain Identity Registry", "Core v1"),
    "GOV-IAM-002": ("Identity and Authority", "Authority, Delegation, Consent and Revocation", "Core v1"),
    "GOV-IAM-003": ("Identity and Authority", "Authorization Decision Engine", "Core v1"),
    "GOV-IAM-004": ("Identity and Authority", "Human Approval and Escalation", "Core v1"),
    "GOV-POL-001": ("Policy", "Policy Registry and Integrity", "Core v1"),
    "GOV-POL-002": ("Policy", "Policy Decision Engine", "Core v1"),
    "GOV-POL-003": ("Policy", "Policy Lifecycle, Amendment and Distribution", "Core v1"),
    "GOV-INF-001": ("Information Governance", "Classification and Labeling", "Core v1"),
    "GOV-INF-002": ("Information Governance", "Information Flow Decision Engine", "Core v1"),
    "GOV-INF-003": ("Information Governance", "Liquid Aperture Release Control", "Core v1"),
    "GOV-INF-004": ("Information Governance", "Schema and Data Contract Registry", "Core v1"),
    "GOV-INF-005": ("Information Governance", "Ingestion Governance and Lineage Coordinator", "Core v1"),
    "GOV-CAP-001": ("Capability Coordination", "Capability Registry", "Core v1"),
    "GOV-CAP-002": ("Capability Coordination", "Capability Authorization and Eligibility", "Core v1"),
    "GOV-CAP-003": ("Capability Coordination", "Governed Action and Execution Order Coordinator", "Core v1"),
    "GOV-EVD-001": ("Evidence and Assurance", "Decision and Cross-Component Evidence Correlation", "Core v1"),
    "GOV-EVD-002": ("Evidence and Assurance", "Governed Outcome Verification and Audit Reconstruction", "Core v1"),
    "GOV-EVD-003": ("Evidence and Assurance", "Attestation Verification and Artifact Assurance", "Core v1"),
    "GOV-ADM-001": ("Administration and Operations", "Govern Control Plane and Configuration", "Core v1"),
    "GOV-ADM-002": ("Administration and Operations", "Health, Observability, Security and Incident Interface", "Core v1"),
    "GOV-FED-001": ("Federation and Domain Exchange", "Federation Gateway and Domain Exchange Coordinator", "Deferred"),
}

CMP = {
    "CMP-CTL-001": ("Contract and Control", "Compute Contract Kernel", "Core v1"),
    "CMP-CTL-002": ("Contract and Control", "Execution Gateway", "Core v1"),
    "CMP-CTL-003": ("Contract and Control", "Control-Plane Coordinator", "Core v1"),
    "CMP-CTL-004": ("Contract and Control", "Node Agent", "Core v1"),
    "CMP-TRU-001": ("Trust and Security", "Hardware Identity", "Core v1"),
    "CMP-TRU-002": ("Trust and Security", "Attestation Gateway", "Core v1"),
    "CMP-TRU-003": ("Trust and Security", "Trust Evaluation", "Core v1"),
    "CMP-TRU-004": ("Trust and Security", "Secure Execution Environment", "Core v1"),
    "CMP-TRU-005": ("Trust and Security", "Artifact Integrity and Supply Chain", "Core v1"),
    "CMP-TRU-006": ("Trust and Security", "Secrets and Key Delivery", "Core v1"),
    "CMP-RES-001": ("Topology and Resources", "Topology Model", "Core v1"),
    "CMP-RES-002": ("Topology and Resources", "Topology Resolver", "Core v1"),
    "CMP-RES-003": ("Topology and Resources", "Resource Model and Inventory", "Core v1"),
    "CMP-RES-004": ("Topology and Resources", "Resource Discovery and Advertisement", "Core v1"),
    "CMP-RES-005": ("Topology and Resources", "Resource Resolver", "Core v1"),
    "CMP-RES-006": ("Topology and Resources", "Allocation and Reservation", "Core v1"),
    "CMP-RES-007": ("Topology and Resources", "Admission, Quota and Lease Manager", "Core v1"),
    "CMP-EXE-001": ("Workload and Execution", "Workload Package Manager", "Core v1"),
    "CMP-EXE-002": ("Workload and Execution", "Native Runtime", "Core v1"),
    "CMP-EXE-003": ("Workload and Execution", "Runtime Adapter Manager", "Core v1"),
    "CMP-EXE-004": ("Workload and Execution", "Scheduler", "Core v1"),
    "CMP-EXE-005": ("Workload and Execution", "Runtime Lifecycle Manager", "Core v1"),
    "CMP-EXE-006": ("Workload and Execution", "Checkpoint and Migration Manager", "Core v1"),
    "CMP-EXE-007": ("Workload and Execution", "Recovery Coordinator", "Core v1"),
    "CMP-DAT-001": ("Data and Connectivity", "Data Staging and Result Collection", "Core v1"),
    "CMP-DAT-002": ("Data and Connectivity", "Network and Data-Movement Controller", "Core v1"),
    "CMP-EVD-001": ("Observation and Evidence", "Observation and Telemetry", "Core v1"),
    "CMP-EVD-002": ("Observation and Evidence", "Evidence Bridge", "Core v1"),
    "CMP-EVD-003": ("Observation and Evidence", "Physical Provenance", "Core v1"),
    "CMP-ECO-001": ("Economics", "Quote and Economic Optimizer", "Validation-gated / later v1 phase"),
}

# Open-decision IDs that gate each component, from the documents' open-decision tables.
GATING = {
    "COG-CORE-002": ["COG-DEC-002", "COG-DEC-003"],
    "COG-CORE-003": ["COG-DEC-004", "COG-DEC-005"],
    "COG-CORE-004": ["COG-DEC-006"],
    "COG-REA-001": ["GOV-DEC-011"],
    "COG-REA-005": ["COG-DEC-007"],
    "COG-CMP-001": ["COG-DEC-008"],
    "COG-CMP-003": ["COG-DEC-009"],
    "COG-CMP-004": ["COG-DEC-010"],
    "COG-CMP-005": ["COG-DEC-009"],
    "COG-ASSUR-002": ["COG-DEC-011"],
    "COG-ASSUR-003": ["COG-DEC-017", "COG-DEC-018"],
    "COG-ASSUR-004": ["COG-DEC-012"],
    "GOV-IAM-001": ["GOV-DEC-003"],
    "GOV-IAM-002": ["GOV-DEC-003", "GOV-DEC-008"],
    "GOV-IAM-003": ["GOV-DEC-004", "GOV-DEC-014"],
    "GOV-IAM-004": ["GOV-DEC-004", "GOV-DEC-018"],
    "GOV-POL-001": ["GOV-DEC-004", "GOV-DEC-007"],
    "GOV-POL-002": ["GOV-DEC-004", "GOV-DEC-014"],
    "GOV-POL-003": ["GOV-DEC-004", "GOV-DEC-007"],
    "GOV-INF-001": ["GOV-DEC-005"],
    "GOV-INF-002": ["GOV-DEC-005"],
    "GOV-INF-003": ["GOV-DEC-006"],
    "GOV-INF-004": ["GOV-DEC-001"],
    "GOV-INF-005": ["GOV-DEC-007"],
    "GOV-EVD-001": ["GOV-DEC-007"],
    "GOV-EVD-002": ["GOV-DEC-007"],
    "GOV-EVD-003": ["GOV-DEC-003", "GOV-DEC-007"],
    "GOV-ADM-001": ["GOV-DEC-009"],
    "GOV-ADM-002": ["GOV-DEC-009"],
    "GOV-FED-001": ["GOV-DEC-011"],
    "CMP-CTL-001": ["CMP-DEC-001"],
    "CMP-CTL-002": ["CMP-DEC-001"],
    "CMP-CTL-003": ["CMP-DEC-002"],
    "CMP-CTL-004": ["CMP-DEC-010"],
    "CMP-TRU-001": ["CMP-DEC-005"],
    "CMP-TRU-002": ["CMP-DEC-005"],
    "CMP-TRU-003": ["CMP-DEC-007"],
    "CMP-TRU-004": ["CMP-DEC-008"],
    "CMP-TRU-005": ["CMP-DEC-009"],
    "CMP-TRU-006": ["CMP-DEC-010"],
    "CMP-RES-001": ["CMP-DEC-006"],
    "CMP-RES-002": ["CMP-DEC-006"],
    "CMP-RES-003": ["CMP-DEC-011"],
    "CMP-RES-004": ["CMP-DEC-011"],
    "CMP-RES-005": ["CMP-DEC-003"],
    "CMP-RES-006": ["CMP-DEC-012"],
    "CMP-RES-007": ["CMP-DEC-012"],
    "CMP-EXE-001": ["CMP-DEC-004"],
    "CMP-EXE-002": ["CMP-DEC-004"],
    "CMP-EXE-003": ["CMP-DEC-004"],
    "CMP-EXE-004": ["CMP-DEC-012"],
    "CMP-EXE-005": ["CMP-DEC-013"],
    "CMP-EXE-006": ["CMP-DEC-013"],
    "CMP-EXE-007": ["CMP-DEC-013"],
    "CMP-DAT-001": ["CMP-DEC-011"],
    "CMP-DAT-002": ["CMP-DEC-011"],
    "CMP-EVD-001": ["CMP-DEC-014"],
    "CMP-EVD-002": ["CMP-DEC-014"],
    "CMP-EVD-003": ["CMP-DEC-014"],
    "CMP-ECO-001": ["CMP-DEC-015"],
}


def entry(layer: str, cid: str, group: str, title: str, release: str) -> dict:
    if layer == "ax":
        invariants = COG_INVARIANTS
        boundary = COG_BOUNDARY
    elif layer == "ag":
        invariants = GOV_INVARIANTS
        boundary = GOV_BOUNDARY
    else:
        invariants = CMP_INVARIANTS
        boundary = CMP_BOUNDARY
    return {
        "id": cid,
        "layer": layer,
        "group": group,
        "title": title,
        "release": release,
        "owned_result": "UNDECIDED",
        "contract": "UNDECIDED",
        "inputs": "UNDECIDED",
        "outputs": "UNDECIDED",
        "operations": "UNDECIDED",
        "tests": "UNDECIDED",
        "invariants": invariants,
        "boundary_contracts": boundary,
        "boundary_invariants": BOUNDARY_INVARIANTS,
        "open_decisions": GATING.get(cid, []),
        "status": "DERIVED",
    }


def main() -> None:
    components = []
    for cid, (grp, title, rel) in COG.items():
        components.append(entry("ax", cid, grp, title, rel))
    for cid, (grp, title, rel) in GOV.items():
        components.append(entry("ag", cid, grp, title, rel))
    for cid, (grp, title, rel) in CMP.items():
        components.append(entry("ac", cid, grp, title, rel))

    doc = {
        "standard": "ASF v1.2",
        "source": [
            "ASF-COG-FAS-001 v1.0",
            "ASF-GOV-FAS-001 v1.0",
            "ASF-CMP-FAS-001 v1.0",
        ],
        "note": (
            "Derived from the three functional architecture specifications. "
            "Fields the documents state are populated. Fields they do not "
            "state are UNDECIDED and carry the governing open-decision IDs."
        ),
        "counts": {
            "ax": len(COG),
            "ag": len(GOV),
            "ac": len(CMP),
            "total": len(COG) + len(GOV) + len(CMP),
        },
        "components": components,
    }
    payload = json.dumps(
        {k: v for k, v in doc.items() if k != "omega_seal"},
        sort_keys=True,
    ).encode("utf-8")
    doc["omega_seal"] = hashlib.sha256(payload).hexdigest()

    OUT.write_text(json.dumps(doc, indent=2))
    print(f"wrote {OUT}")
    print(f"components: {doc['counts']}")
    print(f"seal: {doc['omega_seal']}")
    gated = sum(1 for c in components if c["open_decisions"])
    print(f"components with open-decision gates: {gated}/{len(components)}")


if __name__ == "__main__":
    main()
