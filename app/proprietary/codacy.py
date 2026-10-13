"""Codacy proprietary object.

Wire format: Codacy API v3 /analysis.
    request:  {"repository": "...", "commit": "...", "files": {...}}
    response: {"issues": [{"file": "...", "line": n, "patternId": "...",
                           "category": "...", "level": "...", "message": "..."}]}

Local implementation is a rule-based Python linter emitting the same
shape. Every rule has the uniform signature `rule(tree, src) -> list`.
"""
from __future__ import annotations

import ast
import re
from typing import Any

from app.proprietary.base import ProprietaryObject


# ── rules (all take tree, src) ──────────────────────────────────
def _rule_unused_import(tree: ast.AST, src: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    imported: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                name = (a.asname or a.name.split(".")[0])
                imported[name] = getattr(node, "lineno", 0)
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                name = a.asname or a.name
                imported[name] = getattr(node, "lineno", 0)

    # collect all Name ids used outside import statements
    used: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            cur: Any = node
            while isinstance(cur, ast.Attribute):
                cur = cur.value
            if isinstance(cur, ast.Name):
                used.add(cur.id)

    for name, line in imported.items():
        if name not in used:
            out.append({"line": line, "patternId": "unused_import",
                        "category": "ErrorProne", "level": "Warning",
                        "message": f"unused import {name}"})
    return out


def _rule_bare_except(tree: ast.AST, src: str) -> list[dict[str, Any]]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            out.append({"line": getattr(node, "lineno", 0),
                        "patternId": "bare_except",
                        "category": "ErrorProne", "level": "Error",
                        "message": "bare except clause"})
    return out


def _rule_long_function(tree: ast.AST, src: str,
                        limit: int = 100) -> list[dict[str, Any]]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "end_lineno", node.lineno) - node.lineno
            if body > limit:
                out.append({"line": node.lineno,
                            "patternId": "function_too_long",
                            "category": "Complexity", "level": "Warning",
                            "message": f"function {node.name} is {body} lines"})
    return out


def _rule_todo_comment(tree: ast.AST, src: str) -> list[dict[str, Any]]:
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        if re.search(r"#\s*(TODO|FIXME|XXX)\b", line, re.IGNORECASE):
            out.append({"line": i, "patternId": "todo_comment",
                        "category": "CodeStyle", "level": "Info",
                        "message": "TODO/FIXME marker"})
    return out


RULES: list = [
    _rule_unused_import,
    _rule_bare_except,
    _rule_long_function,
    _rule_todo_comment,
]


def _local_scan(payload: dict[str, Any]) -> dict[str, Any]:
    files = payload.get("files") or {}
    issues: list[dict[str, Any]] = []
    scanned = 0
    for path, src in files.items():
        if not isinstance(src, str):
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            issues.append({"file": path, "line": e.lineno or 0,
                           "patternId": "syntax_error",
                           "category": "ErrorProne", "level": "Error",
                           "message": f"syntax error: {e.msg}"})
            continue
        scanned += 1
        for rule in RULES:
            try:
                for iss in rule(tree, src):
                    iss["file"] = path
                    issues.append(iss)
            except Exception as exc:  # noqa: BLE001
                issues.append({"file": path, "line": 0,
                               "patternId": "rule_error",
                               "category": "Internal", "level": "Error",
                               "message": f"{rule.__name__}: {type(exc).__name__}"})
    return {"repository": payload.get("repository", "local"),
            "commit": payload.get("commit", "HEAD"),
            "files_scanned": scanned,
            "issues": issues,
            "total": len(issues)}


class CodacyObject(ProprietaryObject):
    def __init__(self) -> None:
        super().__init__(
            vendor="codacy",
            env_key="CODACY_API_TOKEN",
            wire_format="codacy-api-v3-analysis",
            local_impl=_local_scan,
            description="Codacy-compatible rule-based local scanner",
        )
