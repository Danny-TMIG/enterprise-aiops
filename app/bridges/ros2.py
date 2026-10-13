"""ROS2 graph model. Extends ROS1 with actions, lifecycle, QoS."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

QOS_PRESETS = {
    "default":       {"reliability": "reliable",  "durability": "volatile",  "history": "keep_last", "depth": 10},
    "sensor_data":   {"reliability": "best_effort","durability": "volatile", "history": "keep_last", "depth": 5},
    "services":      {"reliability": "reliable",  "durability": "volatile",  "history": "keep_last", "depth": 10},
    "parameters":    {"reliability": "reliable",  "durability": "volatile",  "history": "keep_last", "depth": 1000},
    "transient":     {"reliability": "reliable",  "durability": "transient_local", "history": "keep_last", "depth": 10},
}


@dataclass
class Endpoint:
    name: str
    msg_type: str
    qos: str = "default"


@dataclass
class Action:
    name: str
    goal: str
    result: str
    feedback: str


@dataclass
class Node2:
    name: str
    namespace: str = "/"
    pubs: list[Endpoint] = field(default_factory=list)
    subs: list[Endpoint] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    lifecycle: str | None = None  # None | "unconfigured" | "inactive" | "active" | "finalized"

    @property
    def fqn(self) -> str:
        return f"{self.namespace.rstrip('/')}/{self.name}".replace("//", "/")


class ROS2Catalog:
    def __init__(self) -> None:
        self.nodes: dict[str, Node2] = {}

    def add(self, node: Node2) -> Node2:
        self.nodes[node.fqn] = node
        return node

    def qos_mismatches(self) -> list[tuple[str, str]]:
        """Publishers/subscribers on the same topic with incompatible QoS."""
        pub: dict[str, str] = {}
        sub: dict[str, str] = {}
        for n in self.nodes.values():
            for e in n.pubs:
                pub[e.name] = e.qos
            for e in n.subs:
                sub[e.name] = e.qos
        out: list[tuple[str, str]] = []
        for t in set(pub) & set(sub):
            a = QOS_PRESETS.get(pub[t], {})
            b = QOS_PRESETS.get(sub[t], {})
            if a.get("reliability") != b.get("reliability") \
               or a.get("durability") != b.get("durability"):
                out.append((t, f"pub={pub[t]} sub={sub[t]}"))
        return out

    def graph(self) -> dict[str, Any]:
        return {
            "nodes": {k: {
                "pubs": [(e.name, e.msg_type, e.qos) for e in v.pubs],
                "subs": [(e.name, e.msg_type, e.qos) for e in v.subs],
                "actions": [(a.name, a.goal, a.result, a.feedback) for a in v.actions],
                "lifecycle": v.lifecycle,
            } for k, v in self.nodes.items()},
            "qos_mismatches": self.qos_mismatches(),
        }


def runtime_available() -> tuple[bool, str]:
    try:
        import rclpy  # noqa: F401
        return True, "rclpy installed"
    except Exception:
        return False, "rclpy not installed; model layer only"


def describe() -> dict[str, Any]:
    ok, why = runtime_available()
    c = ROS2Catalog()
    c.add(Node2("talker", pubs=[Endpoint("/chatter", "std_msgs/msg/String", "default")]))
    c.add(Node2("listener", subs=[Endpoint("/chatter", "std_msgs/msg/String", "sensor_data")]))
    return {
        "model": "ros2",
        "qos_presets": sorted(QOS_PRESETS),
        "runtime_available": ok,
        "runtime_reason": why,
        "sample_graph": c.graph(),
    }


# ── self-registration ───────────────────────────────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("bridge_ros2")
    def _entry(*args, **kwargs):
        return describe()


_self_register()
