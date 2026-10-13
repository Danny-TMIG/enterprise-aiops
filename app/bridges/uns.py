"""Unified Namespace (ISA-95 / Sparkplug B shape).

A hierarchical topic tree: enterprise/site/area/line/cell/asset/tag.
Pure Python. No broker needed for the model layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

LEVELS = ("enterprise", "site", "area", "line", "cell", "asset", "tag")


@dataclass
class UNSNode:
    level: str
    name: str
    children: dict[str, UNSNode] = field(default_factory=dict)
    payload: dict[str, Any] | None = None

    def path(self, root: str = "") -> str:
        return f"{root}/{self.name}" if root else self.name


class UNSTree:
    def __init__(self, root: str = "enterprise") -> None:
        self.root_name = root
        self.root = UNSNode(level=LEVELS[0], name=root)

    def add(self, path: str, **payload: Any) -> UNSNode:
        """Insert a path like 'acme/plant1/lineA/cell1/robot1/temp'."""
        parts = [p for p in path.strip("/").split("/") if p]
        node = self.root
        for i, name in enumerate(parts):
            lvl = LEVELS[min(i + 1, len(LEVELS) - 1)]
            node = node.children.setdefault(name, UNSNode(level=lvl, name=name))
        if payload:
            node.payload = dict(payload)
        return node

    def prefix(self, path: str) -> list[UNSNode]:
        """All nodes under a given prefix."""
        parts = [p for p in path.strip("/").split("/") if p]
        node = self.root
        for name in parts:
            node = node.children.get(name)
            if node is None:
                return []
        out: list[UNSNode] = []

        def walk(n: UNSNode, acc: str) -> None:
            here = acc + "/" + n.name
            for c in n.children.values():
                out.append(c)
                walk(c, here)
        walk(node, "/" + "/".join([self.root_name] + parts))
        return out

    def topic(self, path: str) -> str:
        return f"spBv1.0/{path.replace(' ', '_')}"

    def snapshot(self) -> dict[str, Any]:
        def dump(n: UNSNode) -> dict[str, Any]:
            return {
                "level": n.level,
                "name": n.name,
                "payload": n.payload,
                "children": {k: dump(v) for k, v in n.children.items()},
            }
        return dump(self.root)


# ── runtime binding ────────────────────────────────────────────────
def runtime_available() -> tuple[bool, str]:
    try:
        import paho.mqtt.client  # noqa: F401
        return True, "paho-mqtt installed"
    except Exception:
        return False, "paho-mqtt not installed; model layer only"


def describe() -> dict[str, Any]:
    ok, why = runtime_available()
    t = UNSTree()
    t.add("acme/plant1/lineA/cell1/robot1/temp", unit="C", value=22.4)
    t.add("acme/plant1/lineA/cell1/robot1/state", value="idle")
    return {
        "model": "unified_namespace",
        "levels": list(LEVELS),
        "runtime_available": ok,
        "runtime_reason": why,
        "sample_topic": t.topic("acme/plant1/lineA/cell1/robot1/temp"),
    }


# ── self-registration ───────────────────────────────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("bridge_uns")
    def _entry(*args, **kwargs):
        return describe()


_self_register()
