"""ASF invariants — properties that must hold in every reachable state.

An invariant is a property of a system that is true initially and
preserved by every permitted transition. It is the strongest of the four
foundational layers: unlike axioms it is provable, unlike postulates it
is not merely posited, unlike predicates it is about states not outputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Invariant:
    id: str
    statement: str
    source: str


INVARIANTS = (
    Invariant("GOV-INV-001", "Cognition cannot authorize its own consequential action.", "Govern FAS"),
    Invariant("GOV-INV-002", "Govern cannot execute a physical workload.", "Govern FAS"),
    Invariant("GOV-INV-003", "Compute cannot broaden an order, substitute a capability, or reinterpret policy.", "Govern FAS"),
    Invariant("GOV-INV-004", "Authority, delegation, consent, and approval are bounded, attributable, time-aware, and revocable.", "Govern FAS"),
    Invariant("GOV-INV-005", "Information movement requires an explicit decision; transformation cannot increase authority.", "Govern FAS"),
    Invariant("GOV-INV-006", "Mandatory constraints determine eligibility before optimization.", "Govern FAS"),
    Invariant("GOV-INV-007", "Every consequential terminal outcome has an immutable, reconstructible evidence chain.", "Govern FAS"),
    Invariant("GOV-INV-008", "Missing identity, authority, policy, classification, integrity, or evidence dependencies fail closed.", "Govern FAS"),
    Invariant("GOV-INV-009", "Historical state and policy are corrected by supersession, not silent mutation.", "Govern FAS"),
    Invariant("GOV-INV-010", "Unvalidated mathematics or research mechanisms are never represented as implemented guarantees.", "Govern FAS"),

    Invariant("CMP-INV-001", "Compute executes only a valid, current, attributable order issued through Govern.", "Compute FAS"),
    Invariant("CMP-INV-002", "Compute cannot broaden authority, relax policy, alter information-flow permission, or substitute a capability.", "Compute FAS"),
    Invariant("CMP-INV-003", "Mandatory authorization, policy, flow, capability, trust, attestation, topology, artifact, and resource conditions are conjunctive.", "Compute FAS"),
    Invariant("CMP-INV-004", "Economic optimization operates only within the eligible set.", "Compute FAS"),
    Invariant("CMP-INV-005", "Every executing workload is bound to one order, workload identity, package version, reservation, node identity, and evidence context.", "Compute FAS"),
    Invariant("CMP-INV-006", "No node or workload participates after its required identity, attestation, trust, lease, artifact, or order validity expires.", "Compute FAS"),
    Invariant("CMP-INV-007", "Cancellation and revocation dominate new dispatch and trigger explicit in-flight handling.", "Compute FAS"),
    Invariant("CMP-INV-008", "Retries, recovery, migration, and projection changes cannot duplicate non-idempotent effects.", "Compute FAS"),
    Invariant("CMP-INV-009", "Protected inputs, outputs, secrets, network flows, and checkpoints remain within their authorized envelope.", "Compute FAS"),
    Invariant("CMP-INV-010", "Every terminal execution state has sufficient typed evidence to show what was attempted, where, with what artifacts, and with which assurance limits.", "Compute FAS"),
    Invariant("CMP-INV-011", "Missing or contradictory mandatory evidence prevents a verified-complete claim.", "Compute FAS"),
    Invariant("CMP-INV-012", "Unvalidated topology, trust, arity, security, ledger, quantum, or economic mechanisms are never represented as production guarantees.", "Compute FAS"),

    Invariant("COG-INV-001", "No model is Cognition; models and solvers are replaceable cognitive substrates.", "Cognition FAS"),
    Invariant("COG-INV-002", "Persistent cognitive state and memory are distinct from prompts, context windows, caches, weights, recurrent state, and execution state.", "Cognition FAS"),
    Invariant("COG-INV-003", "Memory is typed and provenance-bearing; memory is not automatically truth.", "Cognition FAS"),
    Invariant("COG-INV-004", "Reasoning is compositional; it may combine neural, symbolic, numerical, search, proof, simulation, retrieval, or hybrid methods.", "Cognition FAS"),
    Invariant("COG-INV-005", "Proposal remains distinct from authorization; execution remains distinct from semantic verification.", "Cognition FAS"),
    Invariant("COG-INV-006", "Failures, uncertainty, contradiction, denial, abstention, degradation, and incomplete evidence remain visible.", "Cognition FAS"),
    Invariant("COG-INV-007", "Optimization cannot silently change governed semantics, disclosure, eligibility, or assurance.", "Cognition FAS"),
    Invariant("COG-INV-008", "Human control is authenticated through Govern; generated content cannot create authority.", "Cognition FAS"),
    Invariant("COG-INV-009", "Research mechanisms remain nonnormative until their mathematics, validation, and adoption gates are met.", "Cognition FAS"),

    Invariant("ENV-001", "Every boundary object carries the ASF Common Envelope.", "All FAS"),
    Invariant("ENV-002", "Every retry uses a stable idempotency key.", "All FAS"),
    Invariant("ENV-003", "Expired, revoked, malformed, unsupported, unsigned, or context-inconsistent objects fail closed.", "All FAS"),
    Invariant("ENV-004", "Cancellation and revocation remain observable state transitions.", "All FAS"),
    Invariant("ENV-005", "The producer owns semantic validity at emission; the consumer validates independently.", "All FAS"),
)


def by_id(inv_id: str) -> Invariant | None:
    for inv in INVARIANTS:
        if inv.id == inv_id:
            return inv
    return None


def by_source(source: str) -> list[Invariant]:
    return [inv for inv in INVARIANTS if inv.source == source]
