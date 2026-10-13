"""Minimal Agent2Agent (A2A) surface.

Implements:
  - AgentCard (well-known JSON)
  - JSON-RPC methods:
      tasks/send
      tasks/get
      tasks/cancel

The mesh presents itself as an A2A agent so external orchestrators
(Microsoft Copilot, Salesforce Agentforce, ServiceNow, Vertex) can
invoke it as a verification backend.
"""
from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class AgentCard:
    name: str = "tmig-mesh"
    description: str = "Vendor-agnostic verification backend for orchestrators"
    url: str = "http://127.0.0.1:8000/dis/a2a"
    version: str = "0.1.0"
    capabilities: list[str] = field(default_factory=lambda: [
        "verification", "proving", "scanning", "evidence",
    ])
    skills: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "capabilities": self.capabilities,
            "skills": self.skills,
            "protocolVersion": "0.2.0",
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json"],
        }


@dataclass
class A2AServer:
    card: AgentCard
    handlers: dict[str, Callable[[dict[str, Any]], Any]] = field(default_factory=dict)
    tasks: dict[str, dict[str, Any]] = field(default_factory=dict)

    def skill(self, name: str, description: str,
              schema: dict[str, Any] | None = None) -> Callable:
        def deco(fn: Callable[[dict[str, Any]], Any]) -> Callable:
            self.card.skills.append({
                "id": name, "name": name, "description": description,
                "inputSchema": schema or {"type": "object"},
            })
            self.handlers[name] = fn
            return fn
        return deco

    def handle(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if method == "tasks/send":
            return self._send(params)
        if method == "tasks/get":
            tid = params.get("id")
            if tid not in self.tasks:
                raise ValueError(f"unknown task: {tid}")
            return self.tasks[tid]
        if method == "tasks/cancel":
            tid = params.get("id")
            if tid not in self.tasks:
                raise ValueError(f"unknown task: {tid}")
            self.tasks[tid]["status"] = "canceled"
            return self.tasks[tid]
        raise ValueError(f"unknown method: {method}")

    def _send(self, params: dict[str, Any]) -> dict[str, Any]:
        tid = params.get("id") or f"task-{uuid.uuid4().hex[:12]}"
        skill_id = (params.get("skill") or
                    (params.get("message") or {}).get("skill") or
                    params.get("skillId"))
        payload = (params.get("message") or {}).get("params") or params.get("params") or {}
        task = {
            "id": tid, "status": "working",
            "createdAt": _now(), "skill": skill_id,
        }
        self.tasks[tid] = task
        fn = self.handlers.get(skill_id or "")
        if not fn:
            task["status"] = "failed"
            task["error"] = f"unknown skill: {skill_id}"
            return task
        try:
            result = fn(payload)
            task["status"] = "completed"
            task["result"] = result
        except Exception as exc:  # noqa: BLE001
            task["status"] = "failed"
            task["error"] = type(exc).__name__
        task["finishedAt"] = _now()
        return task

    def jsonrpc(self, payload: dict[str, Any]) -> dict[str, Any]:
        rid = payload.get("id")
        try:
            result = self.handle(payload.get("method", ""),
                                 payload.get("params") or {})
            return {"jsonrpc": "2.0", "id": rid, "result": result}
        except Exception as exc:  # noqa: BLE001
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601, "message": str(exc)}}


@dataclass
class A2AClient:
    server: A2AServer
    next_id: int = 1

    def _rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": self.next_id,
                   "method": method, "params": params}
        self.next_id += 1
        return self.server.jsonrpc(payload)

    def card(self) -> dict[str, Any]:
        return self.server.card.to_dict()

    def send(self, skill: str, params: dict[str, Any],
             id_: str | None = None) -> dict[str, Any]:
        r = self._rpc("tasks/send", {"id": id_, "skill": skill, "params": params})
        return r.get("result") or r.get("error") or {}

    def get(self, id_: str) -> dict[str, Any]:
        return self._rpc("tasks/get", {"id": id_})

    def cancel(self, id_: str) -> dict[str, Any]:
        return self._rpc("tasks/cancel", {"id": id_})
