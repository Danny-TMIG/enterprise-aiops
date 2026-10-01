"""ROS1 graph model. Pure Python. Runtime binding honest."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Topic:
    name: str
    msg_type: str = "std_msgs/String"


@dataclass
class Service:
    name: str
    srv_type: str = "std_srvs/Empty"


@dataclass
class Node:
    name: str
    pubs: List[Topic] = field(default_factory=list)
    subs: List[Topic] = field(default_factory=list)
    srvs: List[Service] = field(default_factory=list)


class ROSCatalog:
    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node: Node) -> Node:
        self.nodes[node.name] = node
        return node

    def topics(self) -> Set[str]:
        out: Set[str] = set()
        for n in self.nodes.values():
            out.update(t.name for t in n.pubs)
            out.update(t.name for t in n.subs)
        return out

    def orphan_topics(self) -> List[str]:
        """Published but never subscribed (or vice versa)."""
        produced: Set[str] = set()
        consumed: Set[str] = set()
        for n in self.nodes.values():
            produced.update(t.name for t in n.pubs)
            consumed.update(t.name for t in n.subs)
        return sorted((produced ^ consumed))

    def graph(self) -> Dict[str, Any]:
        return {
            "nodes": {name: {
                "pubs": [t.name for t in n.pubs],
                "subs": [t.name for t in n.subs],
                "srvs": [s.name for s in n.srvs],
            } for name, n in self.nodes.items()},
            "topics": sorted(self.topics()),
            "orphans": self.orphan_topics(),
        }


def runtime_available() -> Tuple[bool, str]:
    try:
        import rospy  # noqa: F401
        return True, "rospy installed"
    except Exception:
        return False, "rospy not installed; model layer only"


def describe() -> Dict[str, Any]:
    ok, why = runtime_available()
    c = ROSCatalog()
    c.add_node(Node("talker", pubs=[Topic("/chatter")]))
    c.add_node(Node("listener", subs=[Topic("/chatter")]))
    return {
        "model": "ros1",
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

    @register("bridge_ros")
    def _entry(*args, **kwargs):
        return describe()


_self_register()
