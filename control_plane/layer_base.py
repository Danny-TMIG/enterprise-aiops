"""Shared base class for all A-Z layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
        raise NotImplementedError
