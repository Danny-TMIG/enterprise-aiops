"""AI governance conformance tests.

Each test looks for an artifact in DCS_AIG_ROOT (default: ./ai-governance).
Absence is failure, presence is not sufficient — the artifact must also
satisfy a minimal shape check. Sources may also attest externally; the
Belnap fold combines them.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("DCS_AIG_ROOT", "./ai-governance"))


def _read(name: str):
    p = ROOT / name
    if not p.exists():
        raise AssertionError(f"missing: {p}")
    return p.read_text()


def _json(name: str):
    return json.loads(_read(name))


def risk_register_exists() -> None:
    data = _json("risks.json")
    assert isinstance(data, list) and data, "risk register empty"


def risk_owners_assigned() -> None:
    for r in _json("risks.json"):
        assert r.get("owner"), f"risk {r.get('id','?')} has no owner"
        assert r.get("mitigation"), f"risk {r.get('id','?')} has no mitigation"


def data_provenance() -> None:
    d = _json("data.json")
    assert d.get("sources"), "no data sources listed"
    for s in d["sources"]:
        assert s.get("name") and s.get("license"), f"incomplete source: {s}"


def bias_examined() -> None:
    d = _json("bias.json")
    assert d.get("examined") is True
    assert d.get("findings") is not None


def technical_docs() -> None:
    d = _read("technical-documentation.md")
    assert len(d) > 500, "technical docs too short to be credible"


def model_card_exists() -> None:
    c = _read("MODEL_CARD.md")
    assert "## " in c, "model card missing sections"


def inference_logging() -> None:
    assert _json("logging.json").get("enabled") is True


def logs_tamper_evident() -> None:
    d = _json("logging.json")
    assert d.get("hash_chain") is True or d.get("signed") is True


def capabilities_documented() -> None:
    c = _read("MODEL_CARD.md")
    assert "Limitations" in c or "Limits" in c, "limits not documented"


def ai_disclosure() -> None:
    assert _json("disclosure.json").get("ui_visible") is True


def human_oversight() -> None:
    d = _json("oversight.json")
    assert d.get("reviewers"), "no named reviewers"
    assert d.get("escalation_path"), "no escalation path"


def kill_switch() -> None:
    assert _json("oversight.json").get("kill_switch") is True


def accuracy_reported() -> None:
    d = _json("evals.json")
    assert d.get("benchmarks"), "no benchmarks reported"


def robustness_tested() -> None:
    d = _json("robustness.json")
    assert d.get("attacks_tested", 0) >= 1


def governance_policy() -> None:
    d = _read("ai-policy.md")
    assert "governance" in d.lower() or "policy" in d.lower()
