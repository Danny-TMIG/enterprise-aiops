#!/usr/bin/env python3
"""derive_schemas.py — derive canonical ASF boundary schemas from the FAS docs.

Only schemas the three documents name and describe with minimum semantic
content are written. Anything the documents do not state is omitted, not
invented. Enum values the documents enumerate are included verbatim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "contracts" / "canonical"
OUT.mkdir(parents=True, exist_ok=True)

DRAFT = "https://json-schema.org/draft/2020-12/schema"

# Common envelope fields, quoted from the documents:
# "schema version, object identity, correlation and causation, cognitive
#  identity and workspace references, sovereign-domain and tenant context,
#  issuer, purpose, classification, event and validity time, provenance,
#  integrity, and evidence references."
COMMON_ENVELOPE = {
    "$schema": DRAFT,
    "$id": "asf.common.envelope.v1",
    "title": "ASF Common Envelope",
    "type": "object",
    "required": [
        "schema_version",
        "object_id",
        "correlation_id",
        "sovereign_domain",
        "issuer",
        "purpose",
        "classification",
        "event_time",
        "integrity",
    ],
    "additionalProperties": False,
    "properties": {
        "schema_version": {"type": "string", "minLength": 1},
        "object_id": {"type": "string", "minLength": 1},
        "correlation_id": {"type": "string", "minLength": 1},
        "causation_id": {"type": "string"},
        "cognitive_identity_ref": {"type": "string"},
        "workspace_ref": {"type": "string"},
        "sovereign_domain": {"type": "string", "minLength": 1},
        "tenant_context": {"type": "string"},
        "issuer": {"type": "string", "minLength": 1},
        "purpose": {"type": "string", "minLength": 1},
        "classification": {"type": "string", "minLength": 1},
        "event_time": {"type": "string", "minLength": 1},
        "validity": {
            "type": "object",
            "properties": {
                "not_before": {"type": "string"},
                "not_after": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "provenance": {"type": "object"},
        "integrity": {
            "type": "object",
            "required": ["algorithm", "digest"],
            "properties": {
                "algorithm": {"type": "string"},
                "digest": {"type": "string"},
                "key_id": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "evidence_refs": {"type": "array", "items": {"type": "string"}},
        "idempotency_key": {"type": "string"},
    },
}

# Govern decision outcomes, enumerated in the Govern doc Section 7.
DECISION_OUTCOME = {
    "type": "string",
    "enum": ["ALLOW", "DENY", "CONDITIONAL", "ESCALATE", "INDETERMINATE"],
}

# Assurance states, enumerated in Govern doc Section 12.
ASSURANCE_STATE = {
    "type": "string",
    "enum": [
        "UNVERIFIED",
        "VERIFIED-BOUNDED",
        "INCOMPLETE",
        "CONTRADICTED",
        "EXPIRED",
        "REVOKED",
    ],
}

# Representation classes, enumerated in Govern doc Section 10.
REPRESENTATION_CLASS = {
    "type": "string",
    "enum": [
        "DENIED",
        "METADATA_ONLY",
        "PROVENANCE_ONLY",
        "AGGREGATED",
        "REDACTED",
        "ANONYMIZED",
        "ABSTRACTED",
        "DERIVED",
        "FULL",
    ],
}

# Reproducibility classes, from Cognition doc Section 13.
REPRODUCIBILITY_CLASS = {
    "type": "string",
    "enum": ["BITWISE", "DETERMINISTIC", "SEMANTIC", "STATISTICAL", "NON-REPRODUCIBLE"],
}

SCHEMAS = {
    # ---- cross-layer control objects --------------------------------
    "common-envelope.schema.json": COMMON_ENVELOPE,
    "asf-error.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.error.v1",
        "title": "ASF Error",
        "type": "object",
        "required": ["code", "category", "correlation_id", "retryable"],
        "additionalProperties": False,
        "properties": {
            "code": {"type": "string", "minLength": 1},
            "category": {"type": "string", "minLength": 1},
            "correlation_id": {"type": "string", "minLength": 1},
            "retryable": {"type": "boolean"},
            "safe_detail": {"type": "string"},
            "evidence_ref": {"type": "string"},
            "envelope": {"$ref": "common-envelope.schema.json"},
        },
    },
    "cancellation-revocation-directive.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.control.cancellation_revocation.v1",
        "title": "CancellationRevocationDirective",
        "type": "object",
        "required": ["envelope", "target", "reason", "authority_ref", "effective_time"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "target": {"type": "string", "minLength": 1},
            "reason": {"type": "string", "minLength": 1},
            "authority_ref": {"type": "string", "minLength": 1},
            "effective_time": {"type": "string", "minLength": 1},
            "requires_acknowledgement": {"type": "boolean"},
        },
    },
    # ---- Govern-emitted contracts -----------------------------------
    "authorization-request.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.authorization_request.v1",
        "title": "AuthorizationRequest",
        "type": "object",
        "required": ["envelope", "subject", "action", "object", "purpose"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "subject": {"type": "string", "minLength": 1},
            "action": {"type": "string", "minLength": 1},
            "object": {"type": "string", "minLength": 1},
            "purpose": {"type": "string", "minLength": 1},
            "context": {"type": "object"},
        },
    },
    "authorization-decision.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.authorization_decision.v1",
        "title": "AuthorizationDecision",
        "type": "object",
        "required": ["envelope", "outcome", "effective_authority_ref", "validity"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "outcome": DECISION_OUTCOME,
            "effective_authority_ref": {"type": "string", "minLength": 1},
            "obligations": {"type": "array", "items": {"type": "string"}},
            "validity": {
                "type": "object",
                "properties": {
                    "not_before": {"type": "string"},
                    "not_after": {"type": "string"},
                },
                "additionalProperties": False,
            },
            "reasons": {"type": "array", "items": {"type": "string"}},
        },
    },
    "information-flow-request.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.information_flow_request.v1",
        "title": "InformationFlowRequest",
        "type": "object",
        "required": ["envelope", "source", "destination", "purpose", "labels"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "source": {"type": "string", "minLength": 1},
            "destination": {"type": "string", "minLength": 1},
            "purpose": {"type": "string", "minLength": 1},
            "labels": {"type": "array", "items": {"type": "string"}},
            "disclosure_budget": {"type": "string"},
            "transform_obligations": {"type": "array", "items": {"type": "string"}},
        },
    },
    "information-flow-decision.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.information_flow_decision.v1",
        "title": "InformationFlowDecision",
        "type": "object",
        "required": ["envelope", "outcome"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "outcome": DECISION_OUTCOME,
            "permitted_representation": REPRESENTATION_CLASS,
            "obligations": {"type": "array", "items": {"type": "string"}},
            "reasons": {"type": "array", "items": {"type": "string"}},
        },
    },
    "representation-request.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.representation_request.v1",
        "title": "RepresentationRequest",
        "type": "object",
        "required": ["envelope", "representation_class", "transformation_plan"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "representation_class": REPRESENTATION_CLASS,
            "transformation_plan": {"type": "object"},
            "verification": {"type": "object"},
            "release_conditions": {"type": "array", "items": {"type": "string"}},
        },
    },
    "capability-request.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.capability_request.v1",
        "title": "CapabilityRequest",
        "type": "object",
        "required": ["envelope", "functional_need", "requested_by"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "functional_need": {"type": "string", "minLength": 1},
            "requested_by": {"type": "string", "minLength": 1},
            "constraints": {"type": "array", "items": {"type": "string"}},
        },
    },
    "governed-capability-set.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.governed_capability_set.v1",
        "title": "GovernedCapabilitySet",
        "type": "object",
        "required": ["envelope", "candidates"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "candidates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["capability_id", "provider_version"],
                    "properties": {
                        "capability_id": {"type": "string"},
                        "provider_version": {"type": "string"},
                    },
                },
            },
            "unsatisfied_constraints": {"type": "array", "items": {"type": "string"}},
        },
    },
    "approval-request.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.approval_request.v1",
        "title": "ApprovalRequest",
        "type": "object",
        "required": ["envelope", "eligible_approvers", "context", "expiry"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "eligible_approvers": {"type": "array", "items": {"type": "string"}},
            "context": {"type": "object"},
            "quorum": {"type": "integer", "minimum": 1},
            "expiry": {"type": "string"},
        },
    },
    "approval-decision.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.approval_decision.v1",
        "title": "ApprovalDecision",
        "type": "object",
        "required": ["envelope", "approver", "decision"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "approver": {"type": "string", "minLength": 1},
            "decision": {"type": "string", "enum": ["APPROVE", "DENY", "ESCALATE", "ABSTAIN"]},
            "reason": {"type": "string"},
        },
    },
    "human-control-presentation.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.cog.human_control_presentation.v1",
        "title": "HumanControlPresentation",
        "type": "object",
        "required": ["envelope", "presentation_id", "subject"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "presentation_id": {"type": "string"},
            "subject": {"type": "object"},
        },
    },
    "human-decision-submission.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.cog.human_decision_submission.v1",
        "title": "HumanDecisionSubmission",
        "type": "object",
        "required": ["envelope", "presentation_ref", "decision"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "presentation_ref": {"type": "string", "minLength": 1},
            "decision": {"type": "string"},
            "reason": {"type": "string"},
        },
    },
    "execution-order.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.execution_order.v1",
        "title": "ExecutionOrder",
        "type": "object",
        "required": [
            "envelope",
            "order_id",
            "authorized_action",
            "capability_ref",
            "bounded_inputs",
            "constraints",
            "evidence_obligations",
        ],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "order_id": {"type": "string", "minLength": 1},
            "authorized_action": {"type": "string", "minLength": 1},
            "capability_ref": {"type": "string", "minLength": 1},
            "bounded_inputs": {"type": "object"},
            "constraints": {"type": "array", "items": {"type": "string"}},
            "evidence_obligations": {"type": "array", "items": {"type": "string"}},
            "validity": {
                "type": "object",
                "properties": {
                    "not_before": {"type": "string"},
                    "not_after": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    },
    "execution-status.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.cmp.execution_status.v1",
        "title": "ExecutionStatus",
        "type": "object",
        "required": ["envelope", "order_ref", "state"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "order_ref": {"type": "string", "minLength": 1},
            "state": {"type": "string", "minLength": 1},
            "detail": {"type": "object"},
        },
    },
    "execution-result.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.cmp.execution_result.v1",
        "title": "ExecutionResult",
        "type": "object",
        "required": ["envelope", "order_ref", "terminal_status"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "order_ref": {"type": "string", "minLength": 1},
            "terminal_status": {"type": "string", "minLength": 1},
            "outputs": {"type": "object"},
            "failure_ref": {"type": "string"},
            "recovery_ref": {"type": "string"},
        },
    },
    "execution-evidence.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.cmp.execution_evidence.v1",
        "title": "ExecutionEvidence",
        "type": "object",
        "required": ["envelope", "order_ref", "claims"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "order_ref": {"type": "string", "minLength": 1},
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["claim_type", "assurance"],
                    "properties": {
                        "claim_type": {"type": "string"},
                        "assurance": ASSURANCE_STATE,
                        "reference": {"type": "string"},
                    },
                },
            },
            "assurance_limits": {"type": "array", "items": {"type": "string"}},
        },
    },
    "governed-outcome.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.governed_outcome.v1",
        "title": "GovernedOutcome",
        "type": "object",
        "required": ["envelope", "verified_status", "evidence_ref"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "verified_status": ASSURANCE_STATE,
            "permitted_representation": REPRESENTATION_CLASS,
            "evidence_ref": {"type": "string", "minLength": 1},
            "limitations": {"type": "array", "items": {"type": "string"}},
        },
    },
    "cognitive-state-update-directive.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.cognitive_state_update_directive.v1",
        "title": "CognitiveStateUpdateDirective",
        "type": "object",
        "required": ["envelope", "target_state_ref", "directive"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "target_state_ref": {"type": "string", "minLength": 1},
            "directive": {"type": "object"},
            "authorized_by": {"type": "string"},
        },
    },
    "knowledge-access-request.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.cog.knowledge_access_request.v1",
        "title": "KnowledgeAccessRequest",
        "type": "object",
        "required": ["envelope", "query", "purpose"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "query": {"type": "object"},
            "purpose": {"type": "string", "minLength": 1},
            "scope": {"type": "array", "items": {"type": "string"}},
        },
    },
    "governed-knowledge-result.schema.json": {
        "$schema": DRAFT,
        "$id": "asf.gov.governed_knowledge_result.v1",
        "title": "GovernedKnowledgeResult",
        "type": "object",
        "required": ["envelope", "representation", "references"],
        "additionalProperties": False,
        "properties": {
            "envelope": {"$ref": "common-envelope.schema.json"},
            "representation": REPRESENTATION_CLASS,
            "references": {"type": "array", "items": {"type": "string"}},
            "provenance": {"type": "object"},
            "limitations": {"type": "array", "items": {"type": "string"}},
        },
    },
}


def main() -> None:
    written = []
    for name, doc in SCHEMAS.items():
        path = OUT / name
        path.write_text(json.dumps(doc, indent=2))
        written.append(name)

    index = {
        "standard": "ASF v1.2",
        "source": [
            "ASF-COG-FAS-001 v1.0 boundary contract alignment",
            "ASF-GOV-FAS-001 v1.0 boundary contract alignment",
            "ASF-CMP-FAS-001 v1.0 boundary contract alignment",
        ],
        "schemas": written,
    }
    payload = json.dumps(index, sort_keys=True).encode("utf-8")
    index["omega_seal"] = hashlib.sha256(payload).hexdigest()
    (OUT / "index.json").write_text(json.dumps(index, indent=2))

    print(f"wrote {len(written)} schemas to {OUT}")
    for n in written:
        print(f"  {n}")
    print(f"seal: {index['omega_seal']}")


if __name__ == "__main__":
    main()
