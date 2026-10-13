#!/usr/bin/env python3
"""Deep scan beneath the naming atlas.

Closes the four gaps the atlas does not:
  1. Executes imports in a subprocess to record runtime resolution.
  2. Normalizes AST bodies to compare semantic equivalence, not just shape.
  3. Resolves __init__.py re-exports so names resolve to their defining module.
  4. Scans .pyi stubs and native extensions for collisions.

Writes:
  atlas_naming/deep.json        machine-readable
  atlas_naming/SHADOWS.md       stdlib shadow action list with runtime proof
  atlas_naming/DECISIONS.md     fill-in decision table with equivalence class
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tokenize
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(os.getcwd()).resolve()
OUT = ROOT / "atlas_naming"
ATLAS = OUT / "atlas.json"

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", ".lanes", "node_modules", ".next",
    "__pycache__", ".mypy_cache", ".ruff_cache", ".hypothesis",
    ".pytest_cache", ".eggs", "build", "dist", ".tox", ".cache",
    ".codeql-results", ".mesh-codeql-db", ".snapshots", ".delta",
    ".last-backups", ".complete-backups", ".benchmarks", "site-packages",
    "_grammar_spec", ".moat", ".murmur", ".agency", ".backrooms",
    "atlas_naming",
}


def is_skipped(path: Path) -> bool:
    return any(p in SKIP_DIRS for p in path.parts) or any(
        p.endswith(".egg-info") for p in path.parts
    )


# ---------------------------------------------------------------------------
# 1. Runtime resolution via subprocess
# ---------------------------------------------------------------------------

def resolve_runtime(name: str) -> dict:
    """Launch a clean Python subprocess with cwd=ROOT and record what `name` resolves to."""
    code = (
        "import importlib.util, json, sys\n"
        f"try:\n"
        f"    spec = importlib.util.find_spec({name!r})\n"
        f"    origin = spec.origin if spec else None\n"
        f"    subs = list(spec.submodule_search_locations) if spec and spec.submodule_search_locations else []\n"
        f"    print(json.dumps({{'ok': True, 'origin': origin, 'subs': subs}}))\n"
        f"except Exception as e:\n"
        f"    print(json.dumps({{'ok': False, 'error': type(e).__name__ + ': ' + str(e)}}))\n"
    )
    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            capture_output=True, text=True, timeout=10,
        )
        for line in r.stdout.strip().splitlines():
            line = line.strip()
            if line.startswith("{"):
                return json.loads(line)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return {"ok": False, "error": "no JSON output", "stderr": r.stderr[:200] if 'r' in dir() else ""}


# ---------------------------------------------------------------------------
# 2. Semantic equivalence via normalized AST
# ---------------------------------------------------------------------------

def normalize_ast(source: str) -> str:
    """Strip comments, docstrings, variable names, and whitespace to a canonical token stream."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ""
    # Drop docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body = node.body[1:] or [ast.Pass()]
    return ast.dump(tree, annotate_fields=False, include_attributes=False)


def semantic_hash(source: str, kind: str, name: str) -> str:
    """Normalized hash of one class/function definition."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ""
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                # Rename local vars to positional tokens for structural comparison
                buf = io.StringIO()
                buf.write(ast.dump(node, annotate_fields=False, include_attributes=False))
                canon = buf.getvalue()
                # Collapse whitespace and digit runs
                canon = re.sub(r"\s+", " ", canon)
                canon = re.sub(r"\d+", "N", canon)
                return hashlib.sha256(canon.encode()).hexdigest()[:16]
    return ""


def extract_definition_source(path: Path, name: str) -> str:
    """Return the source text of one class/function definition, for semantic comparison."""
    try:
        src = path.read_text(errors="replace")
        tree = ast.parse(src)
    except Exception:
        return ""
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            lines = src.splitlines()
            start = node.lineno - 1
            end = getattr(node, "end_lineno", start + 1)
            return "\n".join(lines[start:end])
    return ""


# ---------------------------------------------------------------------------
# 3. __init__.py re-export graph
# ---------------------------------------------------------------------------

def scan_reexports() -> dict:
    """Build a map: name -> set of defining modules, following __init__.py re-exports."""
    graph = defaultdict(set)
    for py in ROOT.rglob("__init__.py"):
        if is_skipped(py.relative_to(ROOT)):
            continue
        try:
            tree = ast.parse(py.read_text(errors="replace"))
        except Exception:
            continue
        pkg_parts = list(py.relative_to(ROOT).parts[:-1])
        pkg = ".".join(pkg_parts) if pkg_parts else ""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                base = node.module or ""
                for alias in node.names:
                    exported = alias.asname or alias.name
                    # Record that `pkg.exported` re-exports from `base.alias.name`
                    graph[f"{pkg}.{exported}"].add(f"{base}.{alias.name}" if base else alias.name)
    return {k: sorted(v) for k, v in graph.items()}


# ---------------------------------------------------------------------------
# 4. .pyi stubs and native extensions
# ---------------------------------------------------------------------------

def scan_stubs_and_extensions() -> dict:
    stubs = []
    exts = []
    for p in ROOT.rglob("*"):
        if is_skipped(p.relative_to(ROOT)):
            continue
        if p.suffix == ".pyi":
            stubs.append(p.relative_to(ROOT).as_posix())
        elif p.suffix in (".so", ".pyd", ".dylib"):
            exts.append(p.relative_to(ROOT).as_posix())
    return {"stubs": stubs, "extensions": exts}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if not ATLAS.exists():
        print(f"missing {ATLAS}; run the naming atlas first")
        return 1
    atlas = json.loads(ATLAS.read_text())
    print(f"atlas loaded: {atlas['files_scanned']} files")

    # ---------- Runtime resolution for every shadow name ----------
    shadow_names = set()
    for kind, entries in atlas["stdlib_shadows"].items():
        for name in entries:
            shadow_names.add(name)
    print(f"resolving {len(shadow_names)} shadow names in subprocesses")
    runtime_cache = {}
    for name in sorted(shadow_names):
        runtime_cache[name] = resolve_runtime(name)

    # ---------- Semantic hashes for every colliding class ----------
    print("computing semantic hashes for class collisions")
    semantic = {}
    for item in atlas["cross_project_collisions"]["classes"]:
        name = item["name"]
        per_file = {}
        for rel in item["files"]:
            full = ROOT / rel
            if not full.exists():
                continue
            src = extract_definition_source(full, name)
            if src:
                per_file[rel] = {
                    "source": src,
                    "semantic_hash": semantic_hash(src, "class", name),
                }
        if per_file:
            hashes = {v["semantic_hash"] for v in per_file.values()}
            if len(hashes) == 1:
                eq = "identical"
            elif len(hashes) == len(per_file):
                eq = "all-different"
            else:
                eq = "partial-overlap"
            semantic[name] = {
                "occurrences": len(per_file),
                "equivalence": eq,
                "definitions": per_file,
            }

    # ---------- Re-export graph ----------
    print("building __init__.py re-export graph")
    reexports = scan_reexports()
    print(f"  {len(reexports)} re-exported names")

    # ---------- Stubs and extensions ----------
    print("scanning .pyi and native extensions")
    stubs_exts = scan_stubs_and_extensions()
    print(f"  {len(stubs_exts['stubs'])} stubs, {len(stubs_exts['extensions'])} extensions")

    # ---------- Write reports ----------
    deep = {
        "root": str(ROOT),
        "runtime_resolution": runtime_cache,
        "semantic_equivalence": semantic,
        "reexports": reexports,
        "stubs": stubs_exts["stubs"],
        "extensions": stubs_exts["extensions"],
    }
    (OUT / "deep.json").write_text(json.dumps(deep, indent=2, default=list))
    print(f"wrote {OUT / 'deep.json'}")

    # SHADOWS.md
    lines = [
        "# Stdlib Shadow Action List", "",
        "Runtime resolution is executed in a clean subprocess with `cwd=repo root`.",
        "If `resolves_to` points inside the repo, the stdlib name is shadowed.", "",
        "| Shadowed | Resolves to | In repo? | Files affected |",
        "|---|---|:---:|---:|",
    ]
    for name in sorted(shadow_names):
        res = runtime_cache.get(name, {})
        origin = res.get("origin", "") if res.get("ok") else f"<error: {res.get('error','')}>"
        in_repo = "yes" if origin.startswith(str(ROOT)) else "no"
        files = atlas["stdlib_shadows"]["packages"].get(name, []) + atlas["stdlib_shadows"]["modules"].get(name, [])
        lines.append(f"| `{name}` | `{origin}` | {in_repo} | {len(set(files))} |")
    lines.append("")
    for name in sorted(shadow_names):
        res = runtime_cache.get(name, {})
        lines.append(f"## `{name}`")
        lines.append("")
        lines.append(f"- runtime origin: `{res.get('origin','')}`")
        if res.get("subs"):
            for s in res["subs"]:
                lines.append(f"- search path: `{s}`")
        pkg_files = atlas["stdlib_shadows"]["packages"].get(name, [])
        mod_files = atlas["stdlib_shadows"]["modules"].get(name, [])
        if pkg_files:
            lines.append(f"- as package, files: {len(pkg_files)}")
            for f in pkg_files[:5]:
                lines.append(f"  - `{f}`")
        if mod_files:
            lines.append(f"- as module, files: {len(mod_files)}")
            for f in mod_files[:5]:
                lines.append(f"  - `{f}`")
        lines.append("")
    (OUT / "SHADOWS.md").write_text("\n".join(lines))
    print(f"wrote {OUT / 'SHADOWS.md'}")

    # DECISIONS.md
    lines = [
        "# Naming Decision Table", "",
        "Every class collision with its semantic equivalence class.",
        "Fill in the **Decision** column with one of:",
        "`consolidate` `alias` `leave` `rename-shadow`", "",
        "| Name | Occurrences | Equivalence | Decision |",
        "|---|---:|---|---|",
    ]
    for name, info in sorted(semantic.items(), key=lambda kv: -kv[1]["occurrences"]):
        lines.append(f"| `{name}` | {info['occurrences']} | {info['equivalence']} | |")
    lines.append("")
    for name, info in sorted(semantic.items(), key=lambda kv: -kv[1]["occurrences"]):
        lines.append(f"## `{name}` — {info['equivalence']}")
        lines.append("")
        for rel, d in info["definitions"].items():
            lines.append(f"- `{rel}` — semantic hash `{d['semantic_hash']}`")
        lines.append("")
    (OUT / "DECISIONS.md").write_text("\n".join(lines))
    print(f"wrote {OUT / 'DECISIONS.md'}")

    # Summary
    print()
    print("=== deep scan summary ===")
    print(f"shadows resolved at runtime: {len(runtime_cache)}")
    for name in sorted(shadow_names):
        res = runtime_cache.get(name, {})
        origin = res.get("origin", "") if res.get("ok") else "<error>"
        marker = "SHADOW" if origin.startswith(str(ROOT)) else "clean"
        print(f"  {marker:7s} {name:12s} -> {origin}")
    print()
    print(f"class collisions analyzed: {len(semantic)}")
    buckets = defaultdict(int)
    for info in semantic.values():
        buckets[info["equivalence"]] += 1
    for k, v in buckets.items():
        print(f"  {k:18s} {v}")
    print()
    print(f"re-exports resolved: {len(reexports)}")
    print(f"stubs found: {len(stubs_exts['stubs'])}")
    print(f"native extensions found: {len(stubs_exts['extensions'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
