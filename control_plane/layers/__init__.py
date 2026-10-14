"""A-Z layer modules — generated dynamically from the manifest."""
from __future__ import annotations

from control_plane.layer_factory import build_registry

LAYER_REGISTRY: dict = build_registry()

__all__ = ["LAYER_REGISTRY"]
