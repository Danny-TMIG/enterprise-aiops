"""CMP-RES-007 — admission, quota, lease manager.

Hierarchical quota per CMP-DEC-012. A lease is admitted only if every
ancestor in the quota tree has room. Leases carry an expiry; a scheduled
reaper releases expired leases.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Optional


class QuotaError(RuntimeError):
    pass


@dataclass
class QuotaNode:
    name: str
    cpu_cores: int
    memory_gb: int
    parent: Optional["QuotaNode"] = None
    children: list["QuotaNode"] = field(default_factory=list)
    cpu_used: int = 0
    mem_used: int = 0

    def add_child(self, name: str, cpu_cores: int, memory_gb: int) -> "QuotaNode":
        if cpu_cores > self.cpu_cores or memory_gb > self.memory_gb:
            raise QuotaError(f"child {name} exceeds parent {self.name}")
        child = QuotaNode(name, cpu_cores, memory_gb, parent=self)
        self.children.append(child)
        return child

    def ancestors(self):
        node = self
        while node:
            yield node
            node = node.parent

    def path(self) -> str:
        parts = []
        node: Optional[QuotaNode] = self
        while node:
            parts.append(node.name)
            node = node.parent
        return "/".join(reversed(parts))


@dataclass
class Lease:
    lease_id: str
    node: QuotaNode
    cpu_cores: int
    memory_gb: int
    expires_at: float

    def is_expired(self, now: Optional[float] = None) -> bool:
        return (now if now is not None else time.time()) >= self.expires_at


class AdmissionController:
    def __init__(self, root: QuotaNode) -> None:
        self._root = root
        self._leases: dict[str, Lease] = {}

    def _find(self, path: str) -> QuotaNode:
        if path == self._root.name:
            return self._root
        parts = path.split("/")[1:]  # strip root name
        node = self._root
        for part in parts:
            for c in node.children:
                if c.name == part:
                    node = c
                    break
            else:
                raise QuotaError(f"no such node: {path}")
        return node

    def request(
        self,
        lease_id: str,
        node_path: str,
        *,
        cpu_cores: int,
        memory_gb: int,
        ttl_seconds: int = 60,
    ) -> Lease:
        if lease_id in self._leases:
            raise QuotaError(f"lease {lease_id} exists")
        if cpu_cores <= 0 or memory_gb <= 0:
            raise QuotaError("lease resources must be positive")
        node = self._find(node_path)
        for anc in node.ancestors():
            if anc.cpu_used + cpu_cores > anc.cpu_cores:
                raise QuotaError(f"cpu quota exceeded at {anc.path()}")
            if anc.mem_used + memory_gb > anc.memory_gb:
                raise QuotaError(f"memory quota exceeded at {anc.path()}")
        for anc in node.ancestors():
            anc.cpu_used += cpu_cores
            anc.mem_used += memory_gb
        lease = Lease(
            lease_id=lease_id,
            node=node,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            expires_at=time.time() + ttl_seconds,
        )
        self._leases[lease_id] = lease
        return lease

    def release(self, lease_id: str) -> None:
        lease = self._leases.pop(lease_id, None)
        if not lease:
            raise QuotaError(f"unknown lease {lease_id}")
        for anc in lease.node.ancestors():
            anc.cpu_used -= lease.cpu_cores
            anc.mem_used -= lease.memory_gb

    def reap_expired(self, now: Optional[float] = None) -> list[str]:
        t = now if now is not None else time.time()
        expired = [lid for lid, l in self._leases.items() if l.is_expired(t)]
        for lid in expired:
            self.release(lid)
        return expired

    def snapshot(self) -> dict:
        def dump(node: QuotaNode) -> dict:
            return {
                "name": node.name,
                "cpu": [node.cpu_used, node.cpu_cores],
                "mem": [node.mem_used, node.memory_gb],
                "children": [dump(c) for c in node.children],
            }
        return dump(self._root)
