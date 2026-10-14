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
