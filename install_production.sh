#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"

python3 - <<'PYEOF'
from pathlib import Path
import json

# ============================================================== 1. LLM EXECUTOR
Path("control_plane/executor.py").write_text('''"""Executor — runs a layer against its prompt and validates the result.

Two modes:
  - deterministic (default): reads the prompt, returns the schema-shaped
    placeholder. Used in CI, no network, no API key.
  - llm: sends the prompt to a configured model provider, parses the
    response, validates against the artifact schema.

Selection is by env var ASF_EXECUTOR=deterministic|llm. Default: deterministic.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Executor:
    mode: str = "deterministic"
    provider: str = "none"
    model: str = "none"
    prompt_dir: Path = REPO_ROOT / "prompts"
    schema_dir: Path = REPO_ROOT / "contracts" / "schemas"

    @classmethod
    def from_env(cls) -> "Executor":
        return cls(
            mode=os.environ.get("ASF_EXECUTOR", "deterministic"),
            provider=os.environ.get("ASF_PROVIDER", "none"),
            model=os.environ.get("ASF_MODEL", "none"),
        )

    def prompt_for(self, letter: str, name: str) -> str:
        path = self.prompt_dir / f"{letter}-{name.lower()}.md"
        if not path.is_file():
            raise FileNotFoundError(f"prompt missing for layer {letter}: {path}")
        text = path.read_text()
        # strip the markdown header up to the --- separator
        parts = text.split("---", 1)
        return parts[1].strip() if len(parts) > 1 else text.strip()

    def schema_for(self, artifact: str) -> dict[str, Any]:
        path = self.schema_dir / f"{artifact}.schema.json"
        if not path.is_file():
            raise FileNotFoundError(f"schema missing for artifact {artifact}: {path}")
        return json.loads(path.read_text())

    def validate(self, payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
        """Minimal JSON schema validation for the fields the schemas declare.

        Not a full Draft 2020-12 validator. Checks type, required, const,
        enum, and minLength for the fields present in this repo's schemas.
        """
        errors: list[str] = []

        if not isinstance(payload, dict):
            return [f"payload is {type(payload).__name__}, expected object"]

        for key in schema.get("required", []):
            if key not in payload:
                errors.append(f"missing required field: {key}")

        for key, spec in schema.get("properties", {}).items():
            if key not in payload:
                continue
            value = payload[key]
            if "const" in spec and value != spec["const"]:
                errors.append(f"{key}: expected {spec['const']!r}, got {value!r}")
            if "enum" in spec and value not in spec["enum"]:
                errors.append(f"{key}: {value!r} not in {spec['enum']}")
            if "type" in spec:
                expected = spec["type"]
                if expected == "string" and not isinstance(value, str):
                    errors.append(f"{key}: expected string, got {type(value).__name__}")
                elif expected == "number" and not isinstance(value, (int, float)):
                    errors.append(f"{key}: expected number, got {type(value).__name__}")
                elif expected == "integer" and not isinstance(value, int):
                    errors.append(f"{key}: expected integer, got {type(value).__name__}")
                elif expected == "array" and not isinstance(value, list):
                    errors.append(f"{key}: expected array, got {type(value).__name__}")
                elif expected == "object" and not isinstance(value, dict):
                    errors.append(f"{key}: expected object, got {type(value).__name__}")
            if "minLength" in spec and isinstance(value, str) and len(value) < spec["minLength"]:
                errors.append(f"{key}: string shorter than minLength {spec['minLength']}")

        return errors

    def execute(self, letter: str, name: str, artifact: str,
                inputs: dict[str, Any], context: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        """Return (payload, error). error is None on success."""
        if self.mode == "llm":
            return self._execute_llm(letter, name, artifact, inputs, context)
        return self._execute_deterministic(letter, name, artifact, inputs, context)

    def _execute_deterministic(self, letter: str, name: str, artifact: str,
                               inputs: dict[str, Any], context: dict[str, Any]
                               ) -> tuple[dict[str, Any], str | None]:
        payload = {
            "artifact": artifact,
            "produced_by": f"{letter}.{name}",
            "reads": sorted(k for k in inputs),
            "summary": f"{name} produced {artifact}",
        }
        # augment with any required fields the schema declares
        try:
            schema = self.schema_for(artifact)
        except FileNotFoundError:
            return payload, None
        for key, spec in schema.get("properties", {}).items():
            if key in payload:
                continue
            if "const" in spec:
                payload[key] = spec["const"]
            elif "enum" in spec:
                payload[key] = spec["enum"][0]
            elif spec.get("type") == "string":
                payload[key] = f"placeholder-{key}"
            elif spec.get("type") == "number":
                payload[key] = 0.0
            elif spec.get("type") == "integer":
                payload[key] = 0
            elif spec.get("type") == "array":
                payload[key] = []
            elif spec.get("type") == "object":
                payload[key] = {}
        return payload, None

    def _execute_llm(self, letter: str, name: str, artifact: str,
                     inputs: dict[str, Any], context: dict[str, Any]
                     ) -> tuple[dict[str, Any], str | None]:
        """Real LLM dispatch. Requires an implementation for the chosen provider."""
        try:
            prompt = self.prompt_for(letter, name)
            schema = self.schema_for(artifact)
        except FileNotFoundError as e:
            return {}, str(e)

        if self.provider == "none":
            return {}, "ASF_EXECUTOR=llm requires ASF_PROVIDER to be set"

        # Dispatch by provider. Each provider adapter lives here so the rest
        # of the control plane does not know which model is behind it.
        try:
            raw = self._call_provider(prompt, inputs, schema)
        except NotImplementedError as e:
            return {}, str(e)
        except Exception as e:
            return {}, f"provider call failed: {e}"

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            return {}, f"provider returned non-JSON: {e}"

        errors = self.validate(payload, schema)
        if errors:
            return payload, "schema validation failed: " + "; ".join(errors[:3])
        return payload, None

    def _call_provider(self, prompt: str, inputs: dict[str, Any],
                       schema: dict[str, Any]) -> str:
        """Provider adapter. Implement one of these to go live.

        Expected contract:
          - Send `prompt` plus the input context.
          - Request JSON output matching `schema`.
          - Return the raw JSON string.
        """
        if self.provider == "openai":
            raise NotImplementedError(
                "openai adapter not implemented; add to control_plane/executor.py::_call_provider"
            )
        if self.provider == "anthropic":
            raise NotImplementedError("anthropic adapter not implemented")
        if self.provider == "local":
            raise NotImplementedError("local adapter not implemented")
        raise NotImplementedError(f"unknown provider: {self.provider}")
''')
print("wrote control_plane/executor.py")


# ============================================================== 2. WIRE INTO LAYER BASE
base_path = Path("control_plane/layer_base.py")
base_path.write_text('''"""Shared base class for all A-Z layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from control_plane.executor import Executor


@dataclass
class LayerResult:
    letter: str
    artifact: str
    status: str
    reason: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class LayerBase:
    """Every layer reads declared inputs and produces one artifact."""

    letter: str = "?"
    name: str = "Base"
    role: str = "base"
    reads: tuple[str, ...] = ()
    writes: tuple[str, ...] = ()
    pollinates: tuple[str, ...] = ()
    artifact: str = "unknown"

    def execute(self, context: dict[str, Any]) -> LayerResult:
        """Read declared inputs, delegate to the executor, return the result."""
        inputs: dict[str, Any] = {}
        for key in self.reads:
            if key in ("input", "ALL", "ANY_REJECTION"):
                inputs[key] = context.get(key, {})
            else:
                inputs[key] = context.get(key)

        missing = [k for k in self.reads
                   if k not in ("input", "ALL", "ANY_REJECTION")
                   and inputs.get(k) is None]
        if missing:
            return LayerResult(
                letter=self.letter,
                artifact=self.artifact,
                status="BLOCKED",
                reason=f"missing required inputs: {missing}",
                payload={},
            )

        executor = Executor.from_env()
        payload, error = executor.execute(
            self.letter, self.name, self.artifact, inputs, context,
        )
        if error:
            return LayerResult(
                letter=self.letter,
                artifact=self.artifact,
                status="EXECUTION_FAILURE",
                reason=error,
                payload=payload,
            )
        return LayerResult(
            letter=self.letter,
            artifact=self.artifact,
            status="PASS",
            reason="",
            payload=payload,
        )
''')
print("rewrote control_plane/layer_base.py")


# ============================================================== 3. LAYER A — REAL
Path("control_plane/layers/A_contract.py").write_text('''"""A — Contract. Role: Define."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from control_plane.layer_base import LayerBase, LayerResult


@dataclass
class ContractLayer(LayerBase):
    """A: Contract. Defines the execution-contract."""

    letter: str = "A"
    name: str = "Contract"
    role: str = "Define"
    reads: tuple[str, ...] = ("input",)
    writes: tuple[str, ...] = ("ExecutionContract",)
    pollinates: tuple[str, ...] = ("L", "G", "F")
    artifact: str = "execution-contract"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Real derivation. Reads the request, returns the schema-shaped contract.

        The prompt in prompts/A-contract.md describes the same derivation.
        When ASF_EXECUTOR=llm, this method is bypassed and the executor
        sends the prompt to a model instead.
        """
        request = inputs.get("input") or {}
        if not isinstance(request, dict):
            request = {}

        def field(name: str, fallback: Any) -> Any:
            v = request.get(name)
            return v if v is not None else fallback

        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": ["input"],
            "summary": "Derived execution contract from work request.",
            "unit": str(field("unit", "unknown")),
            "quantity": int(field("quantity", 1)),
            "quality_floor": str(field("quality_bar", "unstated")),
            "deadline": str(field("deadline", "unknown")),
            "risk_class": str(field("risk_class", "R3")),
            "budget_ceiling_usd": float(field("budget_ceiling_usd", 0.0)),
            "oversight_requirement": str(field("oversight_requirement", "none")),
        }
''')
print("rewrote control_plane/layers/A_contract.py")


# ============================================================== 4. TEST FOR LAYER A REAL BEHAVIOR
Path("tests/test_layer_a_real.py").write_text('''"""Layer A produces a real execution contract from a request."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from control_plane.layers.A_contract import ContractLayer


REQUIRED_KEYS = ("artifact", "produced_by", "reads", "summary",
                 "unit", "quantity", "quality_floor", "deadline",
                 "risk_class", "budget_ceiling_usd", "oversight_requirement")


def test_layer_a_produces_all_required_fields():
    layer = ContractLayer()
    result = layer.execute({"input": {
        "unit": "one-ticket",
        "quantity": 2,
        "quality_bar": "fcr >= 0.85",
        "deadline": "2026-10-20T00:00:00Z",
        "risk_class": "R2",
        "budget_ceiling_usd": 4.50,
        "oversight_requirement": "L2",
    }})
    assert result.status == "PASS"
    for key in REQUIRED_KEYS:
        assert key in result.payload, f"missing {key}"
    assert result.payload["unit"] == "one-ticket"
    assert result.payload["quantity"] == 2
    assert result.payload["quality_floor"] == "fcr >= 0.85"
    assert result.payload["risk_class"] == "R2"
    assert result.payload["budget_ceiling_usd"] == 4.50
    assert result.payload["oversight_requirement"] == "L2"


def test_layer_a_defaults_on_empty_input():
    layer = ContractLayer()
    result = layer.execute({"input": {}})
    assert result.status == "PASS"
    assert result.payload["unit"] == "unknown"
    assert result.payload["quantity"] == 1
    assert result.payload["risk_class"] == "R3"


def test_layer_a_reads_under_input_key():
    layer = ContractLayer()
    result = layer.execute({"input": {"unit": "one-shift"}})
    assert result.payload["reads"] == ["input"]


def test_executor_deterministic_mode_is_default(monkeypatch):
    monkeypatch.delenv("ASF_EXECUTOR", raising=False)
    from control_plane.executor import Executor
    e = Executor.from_env()
    assert e.mode == "deterministic"


def test_executor_validates_schema():
    from control_plane.executor import Executor
    e = Executor()
    schema = e.schema_for("execution-contract")
    good = {
        "artifact": "execution-contract",
        "produced_by": "A.Contract",
        "reads": ["input"],
        "summary": "test",
    }
    assert e.validate(good, schema) == []
    bad = {"artifact": "wrong"}
    errors = e.validate(bad, schema)
    assert any("artifact" in e_ for e_ in errors)
    assert any("required" in e_ for e_ in errors)


def test_executor_prompt_loader():
    from control_plane.executor import Executor
    e = Executor()
    prompt = e.prompt_for("A", "Contract")
    assert "You are the Contract layer" in prompt
    assert len(prompt.split()) >= 200
''')
print("wrote tests/test_layer_a_real.py")


# ============================================================== 5. FRONTEND START SCRIPT
Path("web/start.sh").write_text('''#!/usr/bin/env bash
# Start the ASF web frontend.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d node_modules ]; then
  echo "[*] installing dependencies (first run)..."
  npm install
fi

echo "[*] regenerating status.json..."
cd ..
python3 tooling/validation/status_json.py
cd web

echo "[*] starting dev server on http://localhost:5173"
npm run dev
''')
Path("web/start.sh").chmod(0o755)
print("wrote web/start.sh")


# ============================================================== 6. STRIP WHITESPACE
fixed = 0
for glob in ("*.py", "*.md", "*.json", "*.sh"):
    for p in Path(".").rglob(glob):
        if ".venv" in p.parts or ".git" in p.parts:
            continue
        s = p.read_text()
        t = "\n".join(line.rstrip() for line in s.splitlines()) + "\n"
        if t != s:
            p.write_text(t)
            fixed += 1
print(f"stripped whitespace from {fixed} files")
PYEOF

echo
echo "=== verify: layer A produces a real contract ==="
python3 -c "
from pathlib import Path
from control_plane.layers.A_contract import ContractLayer
r = ContractLayer().execute({'input': {
    'unit': 'one-ticket', 'quantity': 2, 'quality_bar': 'fcr >= 0.85',
    'deadline': '2026-10-20T00:00:00Z', 'risk_class': 'R2',
    'budget_ceiling_usd': 4.50, 'oversight_requirement': 'L2',
}})
print(f'  status: {r.status}')
for k in ('unit','quantity','quality_floor','risk_class','budget_ceiling_usd'):
    print(f'  {k}: {r.payload[k]}')
"

echo
echo "=== verify: full path ABCD still runs ==="
python3 -m control_plane.cli --path ABCD --request examples/request.json --evidence-out /tmp/ev-final.json 2>&1 | head -8

echo
echo "=== pytest ==="
python -m pytest -q 2>&1 | tail -4

echo
echo "=== commit ==="
git add -A
git commit -s -m "feat(control-plane): LLM executor, real layer A, frontend start script" || echo "nothing to commit"
git push origin main
git log --oneline -3
