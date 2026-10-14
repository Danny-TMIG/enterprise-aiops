"""Executor — runs a layer against its prompt and validates the result.

Two modes:
  - deterministic (default): calls the layer's _produce method, then
    validates against the artifact schema.
  - llm: sends the layer's prompt to a configured provider, parses the
    response, validates against the artifact schema.

No placeholders. If the layer has no real implementation, deterministic
mode returns an error. If the LLM response does not match the schema,
llm mode returns an error. Silence is never a substitute for absence.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


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
        parts = text.split("---", 1)
        return parts[1].strip() if len(parts) > 1 else text.strip()

    def schema_for(self, artifact: str) -> dict[str, Any]:
        path = self.schema_dir / f"{artifact}.schema.json"
        if not path.is_file():
            raise FileNotFoundError(f"schema missing for artifact {artifact}: {path}")
        return json.loads(path.read_text())

    def validate(self, payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
        """Minimal JSON schema validation for the fields the schemas declare."""
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
                inputs: dict[str, Any], context: dict[str, Any],
                produce: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None
                ) -> tuple[dict[str, Any], str | None]:
        """Return (payload, error). error is None on success.

        In deterministic mode, `produce` must be provided — it is the
        layer's own implementation. If it returns None, that is a defect,
        not a placeholder opportunity.
        """
        if self.mode == "llm":
            return self._execute_llm(letter, name, artifact, inputs, context)
        return self._execute_deterministic(letter, name, artifact, inputs, context, produce)

    def _execute_deterministic(self, letter: str, name: str, artifact: str,
                               inputs: dict[str, Any], context: dict[str, Any],
                               produce: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None
                               ) -> tuple[dict[str, Any], str | None]:
        if produce is None:
            return {}, f"layer {letter} has no _produce implementation"
        try:
            payload = produce(inputs, context)
        except Exception as e:
            return {}, f"layer {letter} _produce raised: {e}"
        if payload is None:
            return {}, f"layer {letter} _produce returned None"
        if not isinstance(payload, dict):
            return {}, f"layer {letter} _produce returned {type(payload).__name__}, expected dict"
        try:
            schema = self.schema_for(artifact)
        except FileNotFoundError as e:
            return {}, str(e)
        errors = self.validate(payload, schema)
        if errors:
            return payload, "schema validation failed: " + "; ".join(errors[:5])
        return payload, None

    def _execute_llm(self, letter: str, name: str, artifact: str,
                     inputs: dict[str, Any], context: dict[str, Any]
                     ) -> tuple[dict[str, Any], str | None]:
        try:
            prompt = self.prompt_for(letter, name)
            schema = self.schema_for(artifact)
        except FileNotFoundError as e:
            return {}, str(e)

        if self.provider == "none":
            return {}, "ASF_EXECUTOR=llm requires ASF_PROVIDER to be set"

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
            return payload, "schema validation failed: " + "; ".join(errors[:5])
        return payload, None

    def _call_provider(self, prompt: str, inputs: dict[str, Any],
                       schema: dict[str, Any]) -> str:
        """Provider adapter. Implement one to go live.

        Contract:
          - send `prompt` plus `inputs`
          - request JSON output matching `schema`
          - return raw JSON string
        """
        raise NotImplementedError(
            f"provider {self.provider!r} not implemented; "
            f"add to control_plane/executor.py::_call_provider"
        )
