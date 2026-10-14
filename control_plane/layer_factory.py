"""Layer factory — builds LayerBase subclasses from the manifest at import time.

No hand-written layer files. The manifest declares each layer's identity,
inputs, outputs, artifact, engine, and engine parameters. The factory
produces a class for each row. Adding a 27th layer is a manifest change.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from control_plane.layer_base import LayerBase
from control_plane.engines import run_engine


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "contracts" / "layers" / "layer-manifest.json"


def _class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_")) + "Layer"


def make_layer_class(row: dict[str, Any]) -> type[LayerBase]:
    """Produce a LayerBase subclass from one manifest row."""
    letter = row["letter"]
    name = row["name"]
    engine = row.get("logic")
    params = row.get("params", {})

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        if not engine:
            raise NotImplementedError(f"layer {letter} has no logic declared in manifest")
        payload = run_engine(engine, inputs, context, params)
        if not isinstance(payload, dict):
            raise TypeError(f"engine {engine!r} returned {type(payload).__name__}, expected dict")
        payload.setdefault("artifact", self.artifact)
        payload.setdefault("produced_by", f"{self.letter}.{self.name}")
        payload.setdefault("reads", sorted(k for k in inputs))
        payload.setdefault("summary", f"{self.name} produced {self.artifact}")
        return payload

    cls = type(
        _class_name(name),
        (LayerBase,),
        {
            "letter": letter,
            "name": name,
            "role": row.get("role", ""),
            "reads": tuple(row.get("reads", [])),
            "writes": tuple(row.get("writes", [])),
            "pollinates": tuple(row.get("pollinates", [])),
            "artifact": row.get("artifact", "unknown"),
            "_produce": _produce,
        },
    )
    return cls


def load_manifest() -> list[dict[str, Any]]:
    return json.loads(MANIFEST_PATH.read_text())["layers"]


def build_registry() -> dict[str, type[LayerBase]]:
    """Return {letter: layer_class} built fresh from the manifest."""
    registry: dict[str, type[LayerBase]] = {}
    for row in load_manifest():
        registry[row["letter"]] = make_layer_class(row)
    return registry
