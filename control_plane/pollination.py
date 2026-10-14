"""Pollination graph — enforces the read/write rules between A-Z layers."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path


class IllegalPathError(Exception):
    """Raised when a path violates the pollination rules."""


@dataclass
class Layer:
    letter: str
    name: str
    role: str
    reads: list
    writes: list
    pollinates: list
    artifact: str


@dataclass
class PollinationGraph:
    layers: dict = field(default_factory=dict)

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> "PollinationGraph":
        data = json.loads(manifest_path.read_text())
        layers = {}
        for row in data["layers"]:
            layers[row["letter"]] = Layer(
                letter=row["letter"],
                name=row["name"],
                role=row["role"],
                reads=row["reads"],
                writes=row["writes"],
                pollinates=row["pollinates"],
                artifact=row["artifact"],
            )
        return cls(layers=layers)

    def validate_path(self, path: list) -> None:
        """Raise IllegalPathError if the path is not a legal execution order."""
        seen_letters = set()
        produced_artifacts = set()
        for letter in path:
            if letter not in self.layers:
                raise IllegalPathError(f"unknown layer: {letter}")
            layer = self.layers[letter]
            for req in layer.reads:
                if req in ("input", "ALL", "ANY_REJECTION"):
                    continue
                if req not in seen_letters:
                    raise IllegalPathError(
                        f"layer {letter} reads from {req} which is not earlier in the path"
                    )
            seen_letters.add(letter)
            for w in layer.writes:
                produced_artifacts.add(w)

    def produces(self, path: list) -> list:
        out = []
        for letter in path:
            if letter in self.layers:
                out.extend(self.layers[letter].writes)
        return sorted(set(out))

    def legal_prefixes(self) -> list:
        """Every prefix A, AB, ABC, ... ABCDEFGHIJKLMNOPQRSTUVWXYZ."""
        letters = sorted(self.layers.keys())
        return ["".join(letters[:i]) for i in range(1, len(letters) + 1)]

    def is_downstream_read(self, reader: str, writer: str) -> bool:
        """True iff reader reads from writer."""
        if reader not in self.layers:
            return False
        return writer in self.layers[reader].reads
