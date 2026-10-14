"""A-Z layer modules."""
from __future__ import annotations

from importlib import import_module
from pathlib import Path

from control_plane.layer_base import LayerBase

LAYER_REGISTRY: dict[str, type[LayerBase]] = {}


def _discover() -> None:
    here = Path(__file__).parent
    for path in sorted(here.glob("[A-Z]_*.py")):
        module_name = f"control_plane.layers.{path.stem}"
        mod = import_module(module_name)
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if (isinstance(obj, type)
                    and issubclass(obj, LayerBase)
                    and obj is not LayerBase
                    and getattr(obj, "letter", None)):
                LAYER_REGISTRY[obj.letter] = obj


_discover()

__all__ = ["LAYER_REGISTRY"]
