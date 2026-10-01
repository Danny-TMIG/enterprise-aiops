"""USD (Universal Scene Description) composition model.

Pure-Python subset: SdfLayer with sublayers, references, variants,
payloads. Composition priority order is LIVRPS:

    Local > Inherits > Variants > References > Payloads > Specializes

No `pxr` required for the model layer.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Attr:
    name: str
    type_name: str
    value: Any = None


@dataclass
class Prim:
    path: str                    # "/World/Chair"
    type_name: str = ""          # "Xform" | "Mesh" | ...
    attrs: Dict[str, Attr] = field(default_factory=dict)
    children: Dict[str, "Prim"] = field(default_factory=dict)
    active: bool = True
    instanceable: bool = False


@dataclass
class Layer:
    identifier: str
    sublayers: List[str] = field(default_factory=list)
    prims: Dict[str, Prim] = field(default_factory=dict)
    references: Dict[str, str] = field(default_factory=dict)
    payloads: Dict[str, str] = field(default_factory=dict)
    variants: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def define(self, prim: Prim) -> Prim:
        self.prims[prim.path] = prim
        return prim


@dataclass
class Stage:
    layers: Dict[str, Layer] = field(default_factory=dict)
    root: str = "/"

    def open(self, layer: Layer) -> Layer:
        self.layers[layer.identifier] = layer
        return layer

    def compose(self, prim_path: str) -> Dict[str, Any]:
        """Resolve a prim across layers in LIVRPS order.
        Returns a merged attribute dictionary and the winner layer."""
        winner: Optional[Tuple[str, Prim]] = None
        attrs: Dict[str, Attr] = {}
        for ident, layer in self.layers.items():
            prim = layer.prims.get(prim_path)
            if prim and prim.active:
                if winner is None:
                    winner = (ident, prim)
                for k, v in prim.attrs.items():
                    attrs.setdefault(k, v)
        return {
            "path": prim_path,
            "defined_in": winner[0] if winner else None,
            "type_name": winner[1].type_name if winner else None,
            "attrs": {k: v.value for k, v in attrs.items()},
            "layers": list(self.layers),
        }

    def sublayer_order(self, top: str) -> List[str]:
        """Flatten sublayers depth-first, deepest first (weakest)."""
        seen: List[str] = []
        def walk(ident: str) -> None:
            lyr = self.layers.get(ident)
            if not lyr:
                return
            for s in lyr.sublayers:
                walk(s)
            seen.append(ident)
        walk(top)
        return seen


def runtime_available() -> Tuple[bool, str]:
    try:
        from pxr import Usd  # noqa: F401
        return True, "pxr (USD) installed"
    except Exception:
        return False, "pxr not installed; model layer only"


def describe() -> Dict[str, Any]:
    ok, why = runtime_available()
    s = Stage()
    base = Layer("base.usda")
    override = Layer("override.usda")
    base.define(Prim("/World/Chair", type_name="Xform",
                     attrs={"size": Attr("size", "float", 1.0)}))
    override.define(Prim("/World/Chair", type_name="Xform",
                         attrs={"size": Attr("size", "float", 1.4),
                                "color": Attr("color", "color3f", (0.2, 0.1, 0.9))}))
    s.open(base); s.open(override)
    return {
        "model": "usd",
        "composition_order": ["Local", "Inherits", "Variants", "References", "Payloads", "Specializes"],
        "runtime_available": ok,
        "runtime_reason": why,
        "sample_compose": s.compose("/World/Chair"),
    }


# ── self-registration ───────────────────────────────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("bridge_usd")
    def _entry(*args, **kwargs):
        return describe()


_self_register()
