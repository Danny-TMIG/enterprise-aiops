"""Minimal Model Context Protocol surface.

Implements the JSON-RPC methods every MCP host (Claude Desktop, Cursor,
etc.) expects:
    initialize
    tools/list
    tools/call

The mesh exposes its own capabilities as MCP tools — nothing here
depends on the Anthropic SDK.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

PROTOCOL_VERSION = "2024-11-05"


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    fn: Callable[[dict[str, Any]], Any]

    def descriptor(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


@dataclass
class MCPServer:
    name: str = "tmig-mesh"
    version: str = "0.1.0"
    tools: dict[str, MCPTool] = field(default_factory=dict)

    def register(self, tool: MCPTool) -> MCPServer:
        self.tools[tool.name] = tool
        return self

    def handle(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if method == "initialize":
            return {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {"name": self.name, "version": self.version},
                "capabilities": {"tools": {}},
            }
        if method == "tools/list":
            return {"tools": [t.descriptor() for t in self.tools.values()]}
        if method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments") or {}
            tool = self.tools.get(name)
            if not tool:
                return {"isError": True, "content": [
                    {"type": "text", "text": f"unknown tool: {name}"}]}
            try:
                result = tool.fn(args)
                return {"isError": False, "content": [
                    {"type": "text", "text": _to_text(result)}]}
            except Exception as exc:  # noqa: BLE001
                return {"isError": True, "content": [
                    {"type": "text",
                     "text": f"tool error: {type(exc).__name__}"}]}
        raise ValueError(f"unknown method: {method}")

    def jsonrpc(self, payload: dict[str, Any]) -> dict[str, Any]:
        rid = payload.get("id")
        try:
            result = self.handle(payload.get("method", ""),
                                 payload.get("params") or {})
            return {"jsonrpc": "2.0", "id": rid, "result": result}
        except Exception as exc:  # noqa: BLE001
            return {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32601, "message": str(exc)}}


def _to_text(x: Any) -> str:
    import json
    try:
        return json.dumps(x, default=str)
    except Exception:
        return str(x)


@dataclass
class MCPClient:
    """In-process MCP client. Replace `transport` for stdio/HTTP."""
    server: MCPServer
    next_id: int = 1

    def _rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": self.next_id,
                   "method": method, "params": params}
        self.next_id += 1
        return self.server.jsonrpc(payload)

    def initialize(self) -> dict[str, Any]:
        return self._rpc("initialize", {})

    def list_tools(self) -> list[dict[str, Any]]:
        r = self._rpc("tools/list", {})
        return r.get("result", {}).get("tools", [])

    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._rpc("tools/call", {"name": name, "arguments": arguments})
