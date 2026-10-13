"""Pure-Python AST scan — the mesh's always-available scanner.

Produces nodes with shape:
    {"id", "kind", "name", "file", "line", "extra"}
where kind ∈ {module, capability, skill, endpoint, agent, import}.
"""
from __future__ import annotations

import ast
from pathlib import Path

SKIP_DIRS = {
    "__pycache__", ".venv", "venv", ".git", "node_modules",
    ".pytest_cache", ".codeql-db", ".codeql-results",
    "build", "dist", ".mypy_cache", ".ruff_cache",
}


def _node_id(kind: str, name: str, file: str, line: int) -> str:
    return f"{kind}:{name}:{file}:{line}"


def scan(root: str) -> list[dict]:
    root_p = Path(root)
    out: list[dict] = []
    for py in root_p.rglob("*.py"):
        if any(part in SKIP_DIRS for part in py.parts):
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(text)
        except Exception:
            continue
        rel = str(py.relative_to(root_p))
        # module
        mod_name = rel[:-3].replace("/", ".")
        out.append({
            "id": _node_id("module", mod_name, rel, 0),
            "kind": "module", "name": mod_name,
            "file": rel, "line": 0, "extra": [],
        })
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "capability"
                if ast.get_docstring(node):
                    kind = "skill"
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        if dec.func.attr in ("get", "post", "put", "delete", "patch"):
                            kind = "endpoint"
                            break
                out.append({
                    "id": _node_id(kind, node.name, rel, node.lineno),
                    "kind": kind, "name": node.name,
                    "file": rel, "line": node.lineno,
                    "extra": [mod_name],
                })
            elif isinstance(node, ast.ClassDef):
                if any(k in node.name for k in (
                    "Agent", "Runtime", "Mesh", "Server",
                    "Engine", "Router", "Healer", "Watchdog",
                )):
                    out.append({
                        "id": _node_id("agent", node.name, rel, node.lineno),
                        "kind": "agent", "name": node.name,
                        "file": rel, "line": node.lineno,
                        "extra": [mod_name],
                    })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    out.append({
                        "id": _node_id("import", alias.name, rel, node.lineno),
                        "kind": "import", "name": alias.name,
                        "file": rel, "line": node.lineno, "extra": [],
                    })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    out.append({
                        "id": _node_id("import", node.module, rel, node.lineno),
                        "kind": "import", "name": node.module,
                        "file": rel, "line": node.lineno, "extra": [],
                    })
    return out
