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
