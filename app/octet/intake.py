"""Any input → OctetGraph.

The intake is not a parser. It has one job: produce an octet graph
from arbitrary bytes. Text, JSON, images, audio, raw blobs — same
code path. The graph is the input.
"""
from __future__ import annotations

import json
from typing import Any

from app.octet.graph import OctetGraph
from app.octet.octet import G


def from_bytes(b: bytes) -> OctetGraph:
    g = OctetGraph()
    prev_aux = None
    for byte in b:
        n = g.new_node(G, byte)
        if prev_aux is not None:
            g.wire(prev_aux, (n, 0))
        prev_aux = (n, 2)          # chain via aux1
    return g


def from_text(s: str) -> OctetGraph:
    return from_bytes(s.encode("utf-8"))


def _walk(g: OctetGraph, obj: Any, parent_aux):
    """Recursively fold a JSON-like object into a G-tree.
    Every leaf becomes a G node whose value is the leaf byte."""
    if isinstance(obj, dict):
        keys = sorted(obj.keys())
        for k in keys:
            k_node = g.new_node(G, ord(k[0]) if k else 0)
            if parent_aux is not None:
                g.wire(parent_aux, (k_node, 0))
            _walk(g, obj[k], (k_node, 2))
    elif isinstance(obj, list):
        prev = parent_aux
        for item in obj:
            n = g.new_node(G, 0)
            if prev is not None:
                g.wire(prev, (n, 0))
            _walk(g, item, (n, 2))
            prev = (n, 2)
    elif isinstance(obj, str):
        for byte in obj.encode("utf-8"):
            n = g.new_node(G, byte)
            if parent_aux is not None:
                g.wire(parent_aux, (n, 0))
            parent_aux = (n, 2)
    elif isinstance(obj, bool):
        n = g.new_node(G, 1 if obj else 0)
        if parent_aux is not None:
            g.wire(parent_aux, (n, 0))
    elif isinstance(obj, (int, float)):
        for byte in str(obj).encode("utf-8"):
            n = g.new_node(G, byte)
            if parent_aux is not None:
                g.wire(parent_aux, (n, 0))
            parent_aux = (n, 2)
    elif obj is None:
        n = g.new_node(G, 0)
        if parent_aux is not None:
            g.wire(parent_aux, (n, 0))


def from_json(obj: Any) -> OctetGraph:
    g = OctetGraph()
    _walk(g, obj, None)
    return g


def from_any(x: Any) -> OctetGraph:
    if isinstance(x, OctetGraph):
        return x
    if isinstance(x, bytes):
        return from_bytes(x)
    if isinstance(x, str):
        # is it JSON? try; if not, treat as text
        try:
            return from_json(json.loads(x))
        except Exception:
            return from_text(x)
    if isinstance(x, (dict, list)):
        return from_json(x)
    if isinstance(x, (int, float, bool)) or x is None:
        return from_json(x)
    return from_text(repr(x))
