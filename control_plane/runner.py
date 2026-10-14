"""Runner — executes a path through the A-Z layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from control_plane.layers import LAYER_REGISTRY
from control_plane.layer_base import LayerResult
from control_plane.pollination import PollinationGraph, IllegalPathError


@dataclass
class RunResult:
    path: str
    status: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, dict[str, Any]] = field(default_factory=dict)
    halted_at: str | None = None

    def artifact(self, letter: str) -> dict[str, Any] | None:
        return self.artifacts.get(letter)


@dataclass
class Runner:
    graph: PollinationGraph
    max_steps: int = 26

    def run(self, path: str, seed: dict[str, Any] | None = None) -> RunResult:
        letters = list(path)
        try:
            self.graph.validate_path(letters)
        except IllegalPathError as e:
            return RunResult(path=path, status="ILLEGAL_PATH",
                             steps=[{"error": str(e)}], halted_at=letters[0] if letters else None)

        context: dict[str, Any] = {"input": seed or {}}
        result = RunResult(path=path, status="PASS")

        for letter in letters[: self.max_steps]:
            cls = LAYER_REGISTRY.get(letter)
            if cls is None:
                result.status = "BLOCKED"
                result.halted_at = letter
                result.steps.append({
                    "letter": letter, "status": "BLOCKED",
                    "reason": f"no layer registered for {letter}",
                })
                return result

            layer = cls()
            layer_result: LayerResult = layer.execute(context)

            result.steps.append({
                "letter": letter,
                "name": layer.name,
                "role": layer.role,
                "status": layer_result.status,
                "reason": layer_result.reason,
                "artifact": layer_result.artifact,
            })

            if layer_result.status != "PASS":
                result.status = layer_result.status
                result.halted_at = letter
                return result

            # thread this layer's artifact into context so downstream layers
            # can read it by their declared reads
            context[letter] = layer_result.payload
            result.artifacts[letter] = layer_result.payload

        return result
