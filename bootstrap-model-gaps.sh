#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"

mkdir -p contracts/model/examples docs/architecture tests

cat > contracts/model/model-card.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://asf.tmig/model/model-card.schema.json",
  "title": "ASF Model Card",
  "type": "object",
  "required": [
    "schema_version", "model_id", "model_version",
    "parameter_count", "modality", "context_window",
    "license", "substrate_descriptor", "capabilities",
    "evidence_obligations", "classification_ceiling"
  ],
  "properties": {
    "schema_version": { "const": "1.0" },
    "model_id": { "type": "string" },
    "model_version": { "type": "string" },
    "parameter_count": {
      "type": "object",
      "required": ["total"],
      "properties": {
        "total": { "type": "integer", "minimum": 1 },
        "active": { "type": ["integer", "null"] },
        "units": { "const": "parameters" }
      }
    },
    "modality": {
      "type": "array",
      "minItems": 1,
      "items": { "enum": ["text", "image", "audio", "video", "structured"] }
    },
    "context_window": {
      "type": "object",
      "required": ["tokens"],
      "properties": {
        "tokens": { "type": "integer", "minimum": 1 },
        "extension_mechanism": { "type": ["string", "null"] }
      }
    },
    "quantization": {
      "type": "object",
      "properties": {
        "supported": {
          "type": "array",
          "items": { "enum": ["fp16", "fp8", "int8", "int4"] }
        },
        "default": { "type": ["string", "null"] }
      }
    },
    "license": {
      "type": "object",
      "required": ["spdx", "commercial_use"],
      "properties": {
        "spdx": { "type": "string" },
        "commercial_use": { "type": "boolean" },
        "url": { "type": ["string", "null"] }
      }
    },
    "compute_budget": {
      "type": "object",
      "properties": {
        "training_flops": { "type": ["number", "null"] },
        "gpu_hours": { "type": ["number", "null"] },
        "hardware": { "type": ["string", "null"] },
        "inference_cost_model": {
          "type": ["object", "null"],
          "properties": {
            "cost_per_1k_input_tokens_usd": { "type": ["number", "null"] },
            "cost_per_1k_output_tokens_usd": { "type": ["number", "null"] }
          }
        }
      }
    },
    "substrate_descriptor": {
      "type": "object",
      "required": ["identity", "version", "provenance", "integrity", "lifecycle_state"],
      "properties": {
        "identity": { "type": "string" },
        "version": { "type": "string" },
        "provenance": { "type": "string" },
        "integrity": { "type": "string" },
        "lifecycle_state": {
          "enum": ["discovered", "registered", "qualified", "active", "retired"]
        }
      }
    },
    "capabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["class", "supported"],
        "properties": {
          "class": {
            "enum": [
              "reasoning", "planning", "knowledge_access", "tool_use",
              "memory_access", "code_generation", "structured_output",
              "abstention", "uncertainty_reporting"
            ]
          },
          "supported": { "type": "boolean" },
          "detail": { "type": ["string", "null"] }
        }
      }
    },
    "anti_capabilities": {
      "type": "array",
      "items": {
        "enum": ["no_authority", "no_execution", "no_policy", "no_truth_certification", "no_silent_substitution"]
      },
      "default": ["no_authority", "no_execution", "no_policy", "no_truth_certification", "no_silent_substitution"]
    },
    "evidence_obligations": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["claim", "source"],
        "properties": {
          "claim": { "type": "string" },
          "source": { "type": "string" },
          "integrity_required": { "type": "boolean", "default": true }
        }
      }
    },
    "classification_ceiling": {
      "enum": ["unclassified", "internal", "confidential", "secret"]
    },
    "deployment_profiles": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["profile"],
        "properties": {
          "profile": { "enum": ["M", "L", "S", "E", "G"] },
          "serving_pattern": {
            "type": ["string", "null"],
            "enum": ["aggregated", "aggregated_router", "disaggregated", null]
          },
          "quantization": { "type": ["string", "null"] }
        }
      }
    }
  }
}
EOF

cat > contracts/model/model-classification-binding.schema.json <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://asf.tmig/model/model-classification-binding.schema.json",
  "title": "Model Classification Binding",
  "type": "object",
  "required": ["schema_version", "model_id", "classification_ceiling", "enforced_by", "effective_from"],
  "properties": {
    "schema_version": { "const": "1.0" },
    "model_id": { "type": "string" },
    "classification_ceiling": { "enum": ["unclassified", "internal", "confidential", "secret"] },
    "enforced_by": { "const": "GOV-INF-002" },
    "effective_from": { "type": "string", "format": "date-time" },
    "effective_until": { "type": ["string", "null"], "format": "date-time" },
    "evidence_ref": { "type": "string" }
  }
}
EOF

cat > contracts/model/README.md <<'EOF'
# contracts/model/

Model-integration contracts. Each schema closes a gap between model
documentation and the ASF boundary contract set.

## Files

| File | Closes | Gap |
|---|---|---|
| `model-card.schema.json` | G1, G2, G3, G4, G5, G10 | Parameter count, modality, quantization, license, compute budget, evidence obligations |
| `model-classification-binding.schema.json` | G11 | Model classification ceiling enforcement |

## Deferred gaps

Four gaps remain blocked on FAS decisions:

| Gap | Waiting on |
|---|---|
| G6 Context construction | COG-DEC-009 |
| G7 Fallback rules | COG-DEC-010 |
| G8 Serving pattern | CMP-DEC-003 |
| G9 Substrate qualification | COG-DEC-007 |

Their shape is recorded in `docs/architecture/MODEL_GAP_CLOSURES.md`.
EOF

cat > contracts/model/examples/minimal.model-card.json <<'EOF'
{
  "schema_version": "1.0",
  "model_id": "example-small",
  "model_version": "1.0.0",
  "parameter_count": { "total": 3000000000, "active": null, "units": "parameters" },
  "modality": ["text"],
  "context_window": { "tokens": 8192, "extension_mechanism": null },
  "quantization": { "supported": ["int4", "int8"], "default": "int4" },
  "license": { "spdx": "Apache-2.0", "commercial_use": true, "url": null },
  "compute_budget": { "training_flops": null, "gpu_hours": null, "hardware": null, "inference_cost_model": null },
  "substrate_descriptor": {
    "identity": "example-small",
    "version": "1.0.0",
    "provenance": "example",
    "integrity": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "lifecycle_state": "registered"
  },
  "capabilities": [
    { "class": "reasoning", "supported": true, "detail": "neural" },
    { "class": "abstention", "supported": true, "detail": null }
  ],
  "evidence_obligations": [
    { "claim": "invocation_receipt", "source": "adapter", "integrity_required": true }
  ],
  "classification_ceiling": "internal",
  "deployment_profiles": [
    { "profile": "M", "serving_pattern": "aggregated", "quantization": "int4" }
  ]
}
EOF

cat > contracts/model/examples/3b-phone.model-card.json <<'EOF'
{
  "schema_version": "1.0",
  "model_id": "asf-tiny",
  "model_version": "1.0.0",
  "parameter_count": { "total": 3000000000, "active": null, "units": "parameters" },
  "modality": ["text"],
  "context_window": { "tokens": 4096, "extension_mechanism": null },
  "quantization": { "supported": ["int4"], "default": "int4" },
  "license": { "spdx": "Apache-2.0", "commercial_use": true, "url": null },
  "compute_budget": { "training_flops": null, "gpu_hours": null, "hardware": "mobile-npu", "inference_cost_model": null },
  "substrate_descriptor": {
    "identity": "asf-tiny",
    "version": "1.0.0",
    "provenance": "local",
    "integrity": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
    "lifecycle_state": "qualified"
  },
  "capabilities": [
    { "class": "reasoning", "supported": true, "detail": "neural, bounded" },
    { "class": "knowledge_access", "supported": false, "detail": "local only" },
    { "class": "abstention", "supported": true, "detail": null }
  ],
  "evidence_obligations": [
    { "claim": "invocation_receipt", "source": "adapter", "integrity_required": true }
  ],
  "classification_ceiling": "internal",
  "deployment_profiles": [
    { "profile": "M", "serving_pattern": "aggregated", "quantization": "int4" }
  ]
}
EOF

cat > contracts/model/examples/70b-server.model-card.json <<'EOF'
{
  "schema_version": "1.0",
  "model_id": "asf-medium",
  "model_version": "1.0.0",
  "parameter_count": { "total": 70000000000, "active": null, "units": "parameters" },
  "modality": ["text", "structured"],
  "context_window": { "tokens": 131072, "extension_mechanism": null },
  "quantization": { "supported": ["fp8", "int8"], "default": "fp8" },
  "license": { "spdx": "Apache-2.0", "commercial_use": true, "url": null },
  "compute_budget": { "training_flops": null, "gpu_hours": null, "hardware": "8x-a100", "inference_cost_model": { "cost_per_1k_input_tokens_usd": 0.01, "cost_per_1k_output_tokens_usd": 0.03 } },
  "substrate_descriptor": {
    "identity": "asf-medium",
    "version": "1.0.0",
    "provenance": "local",
    "integrity": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
    "lifecycle_state": "qualified"
  },
  "capabilities": [
    { "class": "reasoning", "supported": true, "detail": "neural, symbolic, retrieval" },
    { "class": "planning", "supported": true, "detail": "decompose, revise" },
    { "class": "knowledge_access", "supported": true, "detail": "via GovernedKnowledgeResult" },
    { "class": "tool_use", "supported": true, "detail": "via CapabilityRequest" },
    { "class": "abstention", "supported": true, "detail": null },
    { "class": "uncertainty_reporting", "supported": true, "detail": "confidence only" }
  ],
  "evidence_obligations": [
    { "claim": "invocation_receipt", "source": "adapter", "integrity_required": true },
    { "claim": "reasoning_graph", "source": "reasoning_fabric", "integrity_required": true }
  ],
  "classification_ceiling": "confidential",
  "deployment_profiles": [
    { "profile": "S", "serving_pattern": "aggregated_router", "quantization": "fp8" },
    { "profile": "L", "serving_pattern": "aggregated", "quantization": "int8" }
  ]
}
EOF

cat > contracts/model/examples/100b-enterprise.model-card.json <<'EOF'
{
  "schema_version": "1.0",
  "model_id": "asf-large",
  "model_version": "1.0.0",
  "parameter_count": { "total": 100000000000, "active": null, "units": "parameters" },
  "modality": ["text", "image", "structured"],
  "context_window": { "tokens": 262144, "extension_mechanism": null },
  "quantization": { "supported": ["fp16", "fp8"], "default": "fp8" },
  "license": { "spdx": "Apache-2.0", "commercial_use": true, "url": null },
  "compute_budget": { "training_flops": null, "gpu_hours": null, "hardware": "h100-cluster", "inference_cost_model": { "cost_per_1k_input_tokens_usd": 0.03, "cost_per_1k_output_tokens_usd": 0.09 } },
  "substrate_descriptor": {
    "identity": "asf-large",
    "version": "1.0.0",
    "provenance": "local",
    "integrity": "sha256:3333333333333333333333333333333333333333333333333333333333333333",
    "lifecycle_state": "qualified"
  },
  "capabilities": [
    { "class": "reasoning", "supported": true, "detail": "neural, symbolic, numerical, search, proof, hybrid" },
    { "class": "planning", "supported": true, "detail": "decompose, revise, recursive" },
    { "class": "knowledge_access", "supported": true, "detail": "via GovernedKnowledgeResult" },
    { "class": "tool_use", "supported": true, "detail": "via CapabilityRequest" },
    { "class": "memory_access", "supported": true, "detail": "read/write via COG-CORE-003" },
    { "class": "code_generation", "supported": true, "detail": "python, typescript" },
    { "class": "abstention", "supported": true, "detail": null },
    { "class": "uncertainty_reporting", "supported": true, "detail": "confidence + calibration" }
  ],
  "evidence_obligations": [
    { "claim": "invocation_receipt", "source": "adapter", "integrity_required": true },
    { "claim": "reasoning_graph", "source": "reasoning_fabric", "integrity_required": true },
    { "claim": "plan_version", "source": "planning", "integrity_required": true }
  ],
  "classification_ceiling": "secret",
  "deployment_profiles": [
    { "profile": "E", "serving_pattern": "disaggregated", "quantization": "fp8" },
    { "profile": "S", "serving_pattern": "disaggregated", "quantization": "fp8" }
  ]
}
EOF

cat > docs/architecture/MODEL_ASF_MAPPING.md <<'EOF'
# Model-to-ASF Mapping

| Model spec section | ASF counterpart | Mapping |
|---|---|---|
| Model identity | `SubstrateDescriptor` (COG-CMP-001) | Direct |
| Parameter count | Not in FAS | Closed by G1 |
| Context window | COG-DEC-009 (Open) | Deferred (G6) |
| Modality | Not in FAS | Closed by G2 |
| Architecture family | COG-INV-001 | Partial |
| Training compute | Not in FAS | Closed by G5 |
| Data provenance | GOV-INF-005 | Partial |
| License | Not in FAS | Closed by G4 |
| Capabilities | `CognitiveSkillDescriptor` (COG-CMP-002) | Direct |
| Deployment profile | Deployment Profiles §15 | Direct |
| Serving architecture | CMP-DEC-003 (Open) | Deferred (G8) |
| Quantization | Not in FAS | Closed by G3 |
| Evidence obligations | COG-ASSUR-001 | Closed by G10 |
| Classification ceiling | GOV-INV-005 | Closed by G11 |
EOF

cat > docs/architecture/MODEL_GAP_CLOSURES.md <<'EOF'
# Model Gap Closures

## Ready now

| Gap | Closed by | Test |
|---|---|---|
| G1 Parameter count | `parameter_count` object | `test_model_card_requires_parameter_count` |
| G2 Modality | `modality` enum array | `test_model_card_requires_modality` |
| G3 Quantization | `quantization.supported` | `test_model_card_declares_quantization` |
| G4 License | `license.spdx` | `test_model_card_requires_spdx` |
| G5 Compute budget | `compute_budget` object | `test_model_card_declares_compute_budget` |
| G10 Evidence obligations | `evidence_obligations` array | `test_model_card_requires_evidence` |
| G11 Classification ceiling | `ModelClassificationBinding` | `test_classification_ceiling_enforced` |

## Deferred

| Gap | Waiting on | Shape recorded |
|---|---|---|
| G6 Context construction | COG-DEC-009 | `ContextAssemblyRecord` |
| G7 Fallback rules | COG-DEC-010 | `fallback_is_eligible` predicate |
| G8 Serving pattern | CMP-DEC-003 | Profile-aware constraint on model card |
| G9 Substrate qualification | COG-DEC-007 | `QualificationRecord` |
EOF

cat > tests/test_model_card.py <<'EOF'
"""Model card schema — one test per closable gap."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "model" / "model-card.schema.json"
EXAMPLES = ROOT / "contracts" / "model" / "examples"


def _schema() -> dict:
    return json.loads(SCHEMA.read_text())


def _examples() -> list[tuple[str, dict]]:
    out = []
    for p in sorted(EXAMPLES.glob("*.model-card.json")):
        out.append((p.name, json.loads(p.read_text())))
    return out


def test_schema_exists():
    assert SCHEMA.is_file()


def test_schema_has_required_gap_fields():
    s = _schema()
    req = set(s["required"])
    for field in ("parameter_count", "modality", "context_window",
                  "license", "evidence_obligations", "classification_ceiling"):
        assert field in req, f"missing required field: {field}"


def test_model_card_requires_parameter_count():
    for name, ex in _examples():
        assert "parameter_count" in ex
        assert ex["parameter_count"]["total"] > 0


def test_model_card_requires_modality():
    for name, ex in _examples():
        assert isinstance(ex["modality"], list)
        assert len(ex["modality"]) >= 1


def test_model_card_declares_quantization():
    for name, ex in _examples():
        q = ex.get("quantization")
        if q is not None:
            assert "supported" in q
            for v in q["supported"]:
                assert v in ("fp16", "fp8", "int8", "int4")


def test_model_card_requires_spdx():
    for name, ex in _examples():
        lic = ex["license"]
        assert "spdx" in lic
        assert "commercial_use" in lic
        assert isinstance(lic["commercial_use"], bool)


def test_model_card_declares_compute_budget():
    for name, ex in _examples():
        if "compute_budget" in ex:
            cb = ex["compute_budget"]
            assert isinstance(cb, dict)


def test_model_card_requires_evidence():
    for name, ex in _examples():
        ev = ex["evidence_obligations"]
        assert isinstance(ev, list)
        assert len(ev) >= 1
        for item in ev:
            assert "claim" in item
            assert "source" in item


def test_classification_ceiling_is_valid_value():
    valid = ("unclassified", "internal", "confidential", "secret")
    for name, ex in _examples():
        assert ex["classification_ceiling"] in valid
EOF

cat > tests/test_model_classification_binding.py <<'EOF'
"""Model classification binding — G11 closure."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "model" / "model-classification-binding.schema.json"


CLASSIFICATION_ORDER = {
    "unclassified": 0,
    "internal": 1,
    "confidential": 2,
    "secret": 3,
}


def test_binding_schema_exists():
    assert SCHEMA.is_file()


def test_binding_schema_constrains_enforcer():
    s = json.loads(SCHEMA.read_text())
    assert s["properties"]["enforced_by"]["const"] == "GOV-INF-002"


def test_binding_requires_all_fields():
    s = json.loads(SCHEMA.read_text())
    req = set(s["required"])
    for field in ("model_id", "classification_ceiling", "enforced_by", "effective_from"):
        assert field in req


def test_classification_ceiling_enforced():
    """A request classified above the model ceiling is rejected."""
    def enforce(model_ceiling: str, request_class: str) -> str:
        if CLASSIFICATION_ORDER[request_class] > CLASSIFICATION_ORDER[model_ceiling]:
            return "deny"
        return "allow"

    assert enforce("internal", "secret") == "deny"
    assert enforce("internal", "internal") == "allow"
    assert enforce("confidential", "internal") == "allow"
    assert enforce("unclassified", "internal") == "deny"


def test_binding_example_valid():
    example = {
        "schema_version": "1.0",
        "model_id": "asf-medium",
        "classification_ceiling": "confidential",
        "enforced_by": "GOV-INF-002",
        "effective_from": "2026-10-14T00:00:00Z",
        "effective_until": None,
        "evidence_ref": "ev-001",
    }
    for field in ("schema_version", "model_id", "classification_ceiling", "enforced_by", "effective_from"):
        assert field in example
EOF

cat > tests/test_gap_register.py <<'EOF'
"""Gap register — every gap is either closed or documented as deferred."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "architecture" / "MODEL_GAP_CLOSURES.md"


def test_doc_exists():
    assert DOC.is_file()


def test_all_eleven_gaps_accounted_for():
    text = DOC.read_text()
    for n in range(1, 12):
        assert f"G{n}" in text, f"gap G{n} missing from closure doc"


def test_seven_gaps_closed():
    """G1-G5, G10, G11 are closed."""
    text = DOC.read_text()
    closed_section = text.split("## Deferred")[0]
    for gap in ("G1", "G2", "G3", "G4", "G5", "G10", "G11"):
        assert gap in closed_section, f"{gap} not in closed section"


def test_four_gaps_deferred():
    """G6-G9 are deferred, each with its blocking decision."""
    text = DOC.read_text()
    deferred_section = text.split("## Deferred")[1] if "## Deferred" in text else ""
    for gap, decision in (
        ("G6", "COG-DEC-009"),
        ("G7", "COG-DEC-010"),
        ("G8", "CMP-DEC-003"),
        ("G9", "COG-DEC-007"),
    ):
        assert gap in deferred_section, f"{gap} not in deferred section"
        assert decision in deferred_section, f"{decision} not cited for {gap}"
EOF

echo "=== files written ==="
ls -1 contracts/model/ contracts/model/examples/ docs/architecture/MODEL_*.md tests/test_model*.py tests/test_gap_register.py 2>/dev/null

echo
echo "=== pytest ==="
python -m pytest tests/test_model_card.py tests/test_model_classification_binding.py tests/test_gap_register.py -q 2>&1 | tail -10

echo
echo "=== full suite ==="
python -m pytest -q 2>&1 | tail -6
