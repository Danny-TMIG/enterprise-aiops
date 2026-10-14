#!/usr/bin/env python3
"""propose_options.py — fill proposed options into open decision records."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "decisions"
P = {}
P["COG-DEC-002"] = ("Cognitive identity lifecycle protocol",
 "What protocol binds, recovers, transfers, and terminates cognitive identity under Govern authority?",
 [("A","Govern-issued signed binding keyed to external principal","Simple, auditable"),
  ("B","Hierarchical identity keys with delegated sub-identities","Scales; heavier ceremony"),
  ("C","Cognition stores opaque reference; Govern owns lifecycle","Cleanest boundary")],
 "C","Keeps Cognition out of identity authority; defers to Govern IAM.")
P["COG-DEC-003"] = ("State consistency and convergence algorithm",
 "What algorithm satisfies COG-MATH-003 for online/offline convergence and conflict resolution?",
 [("A","Optimistic concurrency with explicit conflict records","FAS-conformant"),
  ("B","CRDT merge over typed state fields","Auto convergence; per-field work"),
  ("C","Single-writer per identity with explicit handoff","Simple; blocks concurrency")],
 "A","FAS prohibits silent last-write-wins; A is minimal conformant.")
P["COG-DEC-004"] = ("Memory consolidation semantics",
 "What rules govern consolidation of episodic into semantic memory?",
 [("A","Rule-based thresholds","Explainable; needs calibration"),
  ("B","Learned consolidation scoring","Adaptive; unvalidated"),
  ("C","Manual consolidation","Explainable; low coverage")],
 "A","Rule-based matches FAS quarantine of unvalidated mechanisms.")
P["COG-DEC-005"] = ("Memory deletion and restriction policy-to-storage binding",
 "How does a Govern policy decision map to storage-level delete, restrict, or forget?",
 [("A","Policy emits explicit MemoryDirective","Clean contract"),
  ("B","Memory fabric derives from labels only","Loses purpose/retention reasoning")],
 "A","Keeps the decision on the Govern side per GOV-INV-005.")
P["COG-DEC-006"] = ("Semantic equivalence determination",
 "What criteria determine that two representations are equivalent?",
 [("A","Structural equivalence with explicit exceptions","Decidable; limited coverage"),
  ("B","Equivalence classes defined by Govern policy","Governed; depends on GOV-DEC-004"),
  ("C","Embedding similarity with threshold","Wide; unvalidated")],
 "A","FAS quarantines unvalidated similarity; structural is deterministic.")
P["COG-DEC-007"] = ("Evaluation criteria and calibration record format",
 "What schema records evaluation criteria, result, and calibration?",
 [("A","Typed EvaluationResult with criteria/outcome/uncertainty/verification","Matches boundary contracts"),
  ("B","Free-form structured result","Flexible; weak traceability")],
 "A","FAS says evaluation records criteria and evidence.")
P["COG-DEC-008"] = ("Substrate qualification reference format",
 "What artifact format represents a qualified cognitive substrate?",
 [("A","Signed qualification reference with identity/version/profile/evidence","Complete"),
  ("B","Unsigned descriptor with Govern policy ref","Simpler; weaker supply chain")],
 "A","Matches supply-chain assurance; pairs with CMP-DEC-009.")
P["COG-DEC-009"] = ("Adaptation deployment, rollback, and observation model",
 "How are adaptation proposals evaluated, staged, observed, and rolled back?",
 [("A","Staged rollout with per-stage ApprovalRequest and rollback record","Conformant"),
  ("B","Automatic staged rollout within approved bounds","Risks human-approval requirement")],
 "A","FAS says adaptation requires Govern approval and rollback.")
P["COG-DEC-010"] = ("Swarm coordination readiness",
 "Under what conditions does swarm coordination become a supported mechanism?",
 [("A","Remain research-gated","Safest; no swarm in v1"),
  ("B","Bounded swarm for specific task classes","Adds capability; stability risk")],
 "A","FAS says swarms are research-gated.")
P["COG-DEC-011"] = ("Replay manifest format",
 "What fields must a ReplayManifest carry to reconstruct a run?",
 [("A","Exact substrate/state/memory/knowledge/routing/policy refs","Reconstructible"),
  ("B","References only; freeze deferred","Smaller; drift risk")],
 "A","BITWISE/DETERMINISTIC classes require exact frozen state.")
P["COG-DEC-012"] = ("Adversarial cognition security budgets",
 "What per-deployment budgets bound adversarial cognition tests?",
 [("A","Fixed categories from FAS 12 with per-profile intensity","Uniform"),
  ("B","Risk-derived budgets with operator override","Fitted; harder to compare")],
 "A","Comparable evidence across profiles matters more than tunability.")
P["COG-DEC-017"] = ("Cognitive quality and calibration numeric targets",
 "What measurable targets define cognitive quality and calibration per profile?",
 [("A","Declare required per profile; numbers at acceptance","Honest"),
  ("B","Fix numbers in spec","Testable; may stale")],
 "A","FAS leaves numeric targets open.")
P["COG-DEC-018"] = ("Performance profile numeric targets",
 "What numeric availability, latency, throughput, memory, compute, bandwidth, energy, cost targets per profile?",
 [("A","Profile-declared with L as working baseline","Concrete"),
  ("B","Defer numbers to deployment","Flexible; blocks acceptance")],
 "A","Release requires measurable targets.")
P["GOV-DEC-001"] = ("Canonical transport and serialization",
 "What is the canonical wire representation for Govern boundary objects?",
 [("A","JSON with derived canonical schemas","Immediate; universal"),
  ("B","Protobuf primary with JSON projection","Compact; codegen and drift"),
  ("C","Dual representation","Flexible; more surface")],
 "A","Matches derived schemas; preserves $id/$ref integrity.")
P["GOV-DEC-002"] = ("Persistent store technologies and consistency profile",
 "What storage classes back each Govern store, and what consistency does each promise?",
 [("A","SQLite for single-domain v1","Ships now; single-writer"),
  ("B","PostgreSQL with synchronous replication","Multi-writer; operational weight"),
  ("C","Persistence interface with adapters","Flexible; postpones decision")],
 "A","v1 is single sovereign domain; SQLite keeps invariants testable.")
P["GOV-DEC-003"] = ("Credential formats, trust anchors, and recovery ceremony",
 "What credential format and trust anchors establish principal identity, and what is the recovery ceremony?",
 [("A","X.509 from internal CA; dual-control recovery","Standard; heavier"),
  ("B","Ed25519 with split-key recovery","Lightweight; new tooling"),
  ("C","External IdP with Govern-side binding","Offload; external dependency")],
 "A","Standard format; dual-control recovery maps to Govern evidence.")
P["GOV-DEC-004"] = ("Executable policy language, precedence, and conflict operators",
 "What language expresses Govern policy and how are conflicts resolved?",
 [("A","JSON policy, deny-overrides, first-match-wins","Simple; no full formalism"),
  ("B","Cedar or Rego with established evaluator","Mature; external dependency"),
  ("C","Custom DSL under MATH-017","Full control; heavy lift")],
 "B","Cedar/Rego already provide deterministic evaluation and deny-overrides.")
P["GOV-DEC-005"] = ("Default classification lattice and domain extensions",
 "What is the default classification lattice and how do domains extend it?",
 [("A","Four-level lattice with domain-scoped superset","Familiar; extendable"),
  ("B","Partial order defined per domain by policy","Flexible; complicates proofs")],
 "A","Small fixed lattice plus scoped extension satisfies MATH-020.")
P["GOV-DEC-006"] = ("Liquid Aperture transformation assurance per class",
 "What assurance is required per representation class before release?",
 [("A","Class-specific minimums","Precise; per-class validation"),
  ("B","Single tier with class recorded","Simpler; weaker")],
 "A","FAS lists distinct classes with different implications.")
P["GOV-DEC-007"] = ("Evidence storage, retention, redaction, external-ledger role",
 "Where is evidence stored and what role does an external ledger play?",
 [("A","Govern-owned store; external ledger optional projections","FAS-conformant"),
  ("B","External ledger authoritative","FAS excludes")],
 "A","FAS: Compute retains authoritative local evidence.")
P["GOV-DEC-008"] = ("Revocation latency objectives and partition behavior",
 "What revocation propagation latency is required, and what happens under partition?",
 [("A","Fail-closed under partition","Safe; can block work"),
  ("B","Short-lived authorization during partition","Availability; risk acceptance")],
 "A","GOV-INV-008 requires fail-closed on missing dependencies.")
P["GOV-DEC-009"] = ("SLOs, scale envelope, RTO, and RPO",
 "What availability, scale, and durability targets does v1 promise per interface?",
 [("A","Declare required at acceptance; numbers at product","Honest; blocks acceptance"),
  ("B","Fix numbers in spec","Testable; may stale")],
 "A","FAS leaves these open.")
P["GOV-DEC-010"] = ("Reference vertical-slice domain and consequential action",
 "Which domain and which consequential action define the reference slice?",
 [("A","Departmental CPU; governed-knowledge read with approval","Simple; tests pipeline"),
  ("B","Enterprise with state-changing action","Realistic; heavier")],
 "A","Slice proves the chain; A exercises every boundary.")
P["GOV-DEC-011"] = ("Global ASF federation wire protocol",
 "What is the production cross-domain wire protocol and trust negotiation?",
 [("A","Defer; v1 preserves contract compatibility","Keeps v1 shippable"),
  ("B","Design now under MATH-002","Adds scope")],
 "A","FAS marks Deferred.")
P["GOV-DEC-012"] = ("Capability marketplace commercial and trust model",
 "How would a marketplace operate if introduced?",
 [("A","Defer; no marketplace in v1","Narrow; preserves invariants"),
  ("B","Draft trust model now","Broader; no consumer")],
 "A","FAS marks Deferred and excludes from v1.")
P["GOV-DEC-013"] = ("Genesis-derived weighted ethics grammar",
 "Should the weighted ethics grammar determine production behavior?",
 [("A","Remain unvalidated and research-only","Safe"),
  ("B","Adopt after MATH validation","Not yet possible")],
 "A","FAS: unvalidated shall not determine production behavior.")
P["GOV-DEC-014"] = ("Decision and verification determinism requirements",
 "What determinism is required of authorization and policy decisions?",
 [("A","Same inputs and policy version produce identical decisions","Strict"),
  ("B","Bounded nondeterminism","Flexible; complicates MATH-013")],
 "A","Determinism makes decisions reconstructible.")
P["GOV-DEC-015"] = ("Quorum and separation-of-duty semantics",
 "How are quorum and separation of duty enforced for approval?",
 [("A","Explicit quorum, role exclusion, expiry per request","Precise"),
  ("B","Implicit single-approver default","Simpler; violates FAS")],
 "A","FAS requires eligibility, quorum, separation of duty, expiry.")
P["GOV-DEC-016"] = ("Assignment and anomaly model",
 "What assignment and anomaly signals feed Govern decisions?",
 [("A","Deterministic assignment; anomaly evidence-only","Explainable"),
  ("B","Learned anomaly model influencing assignment","Adaptive; unvalidated")],
 "A","FAS quarantines unvalidated mechanisms.")
P["GOV-DEC-017"] = ("Policy consistency and completeness checks",
 "What checks are required before a policy version activates?",
 [("A","Conflict, unreachable-rule, and obligation-closure checks","Prevents latent conflicts"),
  ("B","Warnings only","Faster; unsafe")],
 "A","MATH-017 requires consistency.")
P["GOV-DEC-018"] = ("Risk and threshold calibration",
 "How are risk thresholds calibrated and where do they enter decisions?",
 [("A","Thresholds are policy data via amendment","Governed"),
  ("B","Thresholds in engine config","Bypasses amendment")],
 "A","FAS treats policy as versioned artifacts.")
P["GOV-DEC-019"] = ("Dependency closure and impact reporting",
 "How are dependency closures computed before activation?",
 [("A","Reverse-dependency graph; activation blocked on unresolved consumer","Strong"),
  ("B","Advisory report only","Lighter; weaker")],
 "A","MATH-019 and CI rules point to reverse-dependency gating.")
P["GOV-DEC-020"] = ("Information-flow noninterference proof obligations",
 "What proof obligations accompany information-flow decisions?",
 [("A","Per-decision proof stub","Traceable; overhead"),
  ("B","System-level proof only","Weak per-decision")],
 "A","MATH-021 is M4; per-decision stubs reach code.")
P["GOV-DEC-021"] = ("Disclosure and derivation monotonicity",
 "What is the formal statement of disclosure monotonicity?",
 [("A","Release cannot increase information content under lattice","Concise"),
  ("B","Per-class constraint checks only","Weaker")],
 "A","MATH-023 expects the monotonicity statement.")
P["GOV-DEC-022"] = ("Semantic compatibility and substitutability",
 "When is one capability a valid substitute for another?",
 [("A","Declared by contract version and profile, verified by test vectors","Concrete"),
  ("B","Provider-declared compatibility","Faster; weaker")],
 "A","MATH-024 asks for semantics; test vectors make it checkable.")
P["GOV-DEC-023"] = ("Compositional evidence and assurance calculus",
 "What algebra composes evidence into an assurance claim?",
 [("A","Typed join with explicit CONTRADICTED; no averaging","Conservative"),
  ("B","Weighted aggregation","Not conformant")],
 "A","FAS says correlation does not transform claim types.")
P["GOV-DEC-024"] = ("Privacy-utility bounds for Liquid Aperture",
 "What bounds define acceptable privacy-utility tradeoff per class?",
 [("A","Per-class residual-risk bound declared as policy","Precise"),
  ("B","Single global bound","Ignores class differences")],
 "A","MATH-026 expects per-class bounds.")
P["GOV-DEC-025"] = ("Transformation and verification assurance",
 "What assurance is required that a transformation produced the claimed class?",
 [("A","Transform-specific verification harness producing signed result","Strong"),
  ("B","Attestation by transform implementation only","Lighter; weaker")],
 "A","MATH-027 and FAS release-control shape require verification.")
P["GOV-DEC-026"] = ("Multi-constraint capability eligibility semantics",
 "What algebra combines authority, policy, flow, assurance, jurisdiction, evidence constraints?",
 [("A","Conjunctive over mandatory; ranking only within eligible set","Matches invariants"),
  ("B","Weighted scoring with thresholds","Rejected by GOV-INV-006")],
 "A","Two FAS documents state constraints are conjunctive.")
P["CMP-DEC-001"] = ("Canonical serialization and transport for Compute",
 "What is the canonical serialization for Compute boundary objects?",
 [("A","Same JSON canonical as Govern","One boundary representation"),
  ("B","Protobuf primary","Compact; drift")],
 "A","Consistency with GOV-DEC-001 removes a projection layer.")
P["CMP-DEC-002"] = ("Control-plane consistency and reconciliation",
 "What consistency model does the Compute control plane provide under partition?",
 [("A","Single-leader with leases; fail-closed on uncertainty","Matches FAS"),
  ("B","Active-active with CRDTs","Heavier")],
 "A","FAS states leases and reconciliation for control-plane uncertainty.")
P["CMP-DEC-003"] = ("Reference v1 deployment topology and scale envelope",
 "What is the reference v1 topology and scale envelope?",
 [("A","Single-domain CPU-only cluster per profile","Matches departmental profile"),
  ("B","Large-scale envelope now","Premature")],
 "A","FAS names departmental CPU as first profile.")
P["CMP-DEC-004"] = ("Initial workload formats",
 "Which workload formats are supported at v1?",
 [("A","Containers (OCI) only","One adapter surface; narrow"),
  ("B","Containers and batch","Two lifecycle models"),
  ("C","Containers, VMs, batch","Widest; most complexity")],
 "A","One format lets EXE/DAT/TRU converge; additive later.")
P["CMP-DEC-005"] = ("Supported CPU/GPU platforms and hardware trust",
 "Which platforms are qualified, and what hardware trust mechanisms are required?",
 [("A","Apple Silicon and x86_64 with TPM 2.0","Practical; excludes some"),
  ("B","Confidential-compute platforms only","Strong trust; tiny base")],
 "A","Reference substrate is Apple Silicon; x86_64/TPM adds a second platform.")
P["CMP-DEC-006"] = ("Topology representation beyond conventional labels",
 "Is any representation beyond conventional labels/graphs adopted?",
 [("A","Conventional graph only","Safe"),
  ("B","Adopt 48-D now","Rejected by FAS")],
 "A","FAS: no 48-D dependency until CMP-MATH-004 meets its gate.")
P["CMP-DEC-007"] = ("Trust-gradient thresholds and graded arity",
 "Are trust-gradient thresholds and graded arity adopted?",
 [("A","Remain unvalidated","Safe"),
  ("B","Adopt after MATH-005/006/008 M4","Future")],
 "A","FAS states trust is a qualification decision.")
P["CMP-DEC-008"] = ("Confidential-compute profiles and required assurances",
 "Which confidential-compute profiles are required?",
 [("A","Optional at v1","Broad support"),
  ("B","Require one specific profile","Narrow hardware")],
 "A","v1 slice does not require confidential compute.")
P["CMP-DEC-009"] = ("Artifact formats, signing roots, provenance, SBOM",
 "What artifact formats, signing roots, provenance format, SBOM policy?",
 [("A","OCI; Sigstore; SLSA-style provenance; SPDX SBOM","Standard, toolable"),
  ("B","Internal signing with custom provenance","In-house; adoption cost")],
 "A","Established formats reduce custom assurance work.")
P["CMP-DEC-010"] = ("Secret provider interface and workload identity",
 "What secret provider interface and workload identity mechanism are used?",
 [("A","SPIFFE/SPIRE; Vault-compatible; short-lived leases","Standard"),
  ("B","Node-local identity with OS keystore","Self-contained")],
 "A","SPIFFE identity and short-lived leases match CMP-INV-005/006.")
P["CMP-DEC-011"] = ("Storage, staging, network, data-transfer technologies",
 "What technologies implement staging, movement, and network control?",
 [("A","S3-compatible staging; mTLS; default-deny policy","Portable"),
  ("B","Custom transfer daemon","Full control; more code")],
 "A","Matches FAS default-deny and authorized-reference staging.")
P["CMP-DEC-012"] = ("Quota hierarchy, scheduling classes, fairness, preemption, reserve",
 "What quota and scheduling model applies?",
 [("A","Hierarchical quota; non-preemptive default","Predictable"),
  ("B","Preemptive priority classes","Higher utilization; harder to verify")],
 "A","MATH-015 preemption safety is heavy; non-preemptive default is minimal conformant.")
P["CMP-DEC-013"] = ("Checkpoint portability, migration guarantees, non-idempotent recovery",
 "What guarantees do checkpoint, migration, and recovery provide?",
 [("A","Workload-declared semantics; migration best-effort","Honest"),
  ("B","Guarantee portability for all workloads","Not generally achievable")],
 "A","CMP-INV-008 requires workload-declared semantics.")
P["CMP-DEC-014"] = ("Evidence retention, provenance store, CAPSTONE role",
 "Where is evidence stored and what role does CAPSTONE or another ledger play?",
 [("A","Compute-owned store; ledger optional sealed projections","FAS-conformant"),
  ("B","Ledger authoritative","Rejected by FAS")],
 "A","FAS: Compute retains authoritative local evidence.")
P["CMP-DEC-015"] = ("Economic optimizer inclusion and calibration gate",
 "Is the economic optimizer included in v1, and under what calibration gate?",
 [("A","Excluded from v1; enabled later under gate","Safe"),
  ("B","Include with unvalidated estimates","Rejected by FAS")],
 "A","FAS: first-release baseline operates without an unvalidated optimizer.")
P["CMP-DEC-016"] = ("Availability, latency, throughput, revocation, RTO, RPO",
 "What numeric targets apply to Compute?",
 [("A","Declared per profile at acceptance","Honest"),
  ("B","Fix numbers in spec","Testable; may stale")],
 "A","FAS leaves these targets to the deployment profile decision.")
P["CMP-DEC-017"] = ("Direct federated cross-domain resource execution",
 "When is direct cross-domain resource execution supported?",
 [("A","Defer to later release","Matches FAS"),
  ("B","Support now","No approved protocol")],
 "A","FAS marks Deferred.")
P["CMP-DEC-018"] = ("QPU resource and hybrid execution support",
 "Is QPU support in scope?",
 [("A","Deferred; no QPU path in v1","Matches FAS"),
  ("B","Include QPU resource class now","Premature")],
 "A","FAS marks Deferred.")
P["CMP-DEC-019"] = ("SHGP or other novel secure-execution mechanism",
 "Is any novel secure-execution mechanism adopted?",
 [("A","Remain unvalidated","Safe"),
  ("B","Adopt after independent security review","Future")],
 "A","FAS marks Unvalidated.")


def main():
    if not DECISIONS.exists():
        print("decisions/ missing; run init_workbook.py first")
        return 2
    n = 0
    for p in sorted(DECISIONS.glob("*.json")):
        rec = json.loads(p.read_text())
        did = rec.get("decision_id")
        if did not in P:
            continue
        title, question, opts, reco, why = P[did]
        rec["title"] = title
        rec["question"] = question
        rec["options"] = [{"id": i, "summary": s, "tradeoffs": t} for i, s, t in opts]
        rec["recommendation"] = reco
        rec["recommendation_reasoning"] = why
        rec["status"] = "OPEN"
        payload = json.dumps(
            {k: v for k, v in rec.items() if k != "record_seal"},
            sort_keys=True
        ).encode()
        rec["record_seal"] = hashlib.sha256(payload).hexdigest()
        p.write_text(json.dumps(rec, indent=2))
        n += 1
    print(f"proposed options written for {n} decisions")
    print("records remain OPEN — close.py is the only thing that closes one")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
