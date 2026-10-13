#!/usr/bin/env python3
"""Stdlib mastery: what your tree uses from the standard library.

For every stdlib module name, computes:
  - which files in the tree import it
  - whether any of them are shadowable (a same-named local file would win)
  - what fraction of stdlib is used vs unused
  - which stdlib names are imported but never referenced (dead imports)
  - which names are used under an alias (import X as Y) and would break under rename

Writes:
  atlas_naming/stdlib.json       machine-readable
  atlas_naming/STDLIB.md         human-readable report
"""
from __future__ import annotations

import ast
import json
import os
import sys
import sysconfig
from collections import defaultdict
from pathlib import Path

ROOT = Path.cwd().resolve()
OUT = ROOT / "atlas_naming"
OUT.mkdir(exist_ok=True)

# The complete stdlib name list, computed from the running interpreter.
STDLIB_DIR = Path(sysconfig.get_paths()["stdlib"])
STDLIB_PATHS = sorted(STDLIB_DIR.glob("*.py"))

BUILTIN_MODULE_NAMES = set(sys.builtin_module_names)

STDLIB_MODULES = set()
for p in STDLIB_PATHS:
    if p.stem == "__init__":
        continue
    if p.stem.startswith("_"):
        continue
    STDLIB_MODULES.add(p.stem)

for d in STDLIB_DIR.iterdir():
    if not d.is_dir() or d.name.startswith("_"):
        continue
    if (d / "__init__.py").exists():
        STDLIB_MODULES.add(d.name)

# Add builtins exposed as modules.
STDLIB_MODULES |= BUILTIN_MODULE_NAMES

# Sub-modules of stdlib packages the tree might import directly.
# Example: `from email.mime.text import MIMEText` -> we want to record `email`.
KNOWN_STDLIB_TOP = frozenset(STDLIB_MODULES)

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", ".lanes", "node_modules", ".next",
    "__pycache__", ".mypy_cache", ".ruff_cache", ".hypothesis",
    ".pytest_cache", ".eggs", "build", "dist", ".tox", ".cache",
    ".codeql-results", ".mesh-codeql-db", ".snapshots", ".delta",
    ".last-backups", ".complete-backups", ".benchmarks", "site-packages",
    "_grammar_spec", ".moat", ".murmur", ".agency", ".backrooms",
    "atlas_naming",
}


def skipped(p: Path) -> bool:
    return any(x in SKIP_DIRS for x in p.parts) or any(
        x.endswith(".egg-info") for x in p.parts
    )


def extract_imports(tree: ast.AST) -> list[dict]:
    """Return every import statement with its form and names."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                out.append({
                    "form": "import",
                    "module": alias.name,
                    "top": top,
                    "asname": alias.asname,
                    "lineno": node.lineno,
                    "bound_name": alias.asname or alias.name.split(".")[0],
                })
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                # relative import, not stdlib
                continue
            base = node.module or ""
            top = base.split(".")[0]
            for alias in node.names:
                out.append({
                    "form": "from",
                    "module": base,
                    "top": top,
                    "name": alias.name,
                    "asname": alias.asname,
                    "lineno": node.lineno,
                    "bound_name": alias.asname or alias.name,
                })
    return out


def used_names(tree: ast.AST) -> set[str]:
    """Names actually referenced in the module body (not just imported)."""
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            # Walk down to the base Name
            current = node
            while isinstance(current, ast.Attribute):
                current = current.value
            if isinstance(current, ast.Name):
                used.add(current.id)
    return used


def classify_shadow(name: str) -> dict:
    """Is `name` shadowable by a same-named file or directory anywhere in the tree?"""
    top_hit = ROOT / name
    top_hit_py = ROOT / f"{name}.py"
    top_hit_pkg = top_hit if top_hit.is_dir() and (top_hit / "__init__.py").exists() else None
    nested_hits = []
    for p in ROOT.rglob(name):
        if skipped(p.relative_to(ROOT)):
            continue
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if rel == Path(name):
            continue
        if p.is_file() and p.suffix == ".py" and p.stem == name:
            nested_hits.append(rel.as_posix())
        elif p.is_dir() and (p / "__init__.py").exists():
            nested_hits.append(rel.as_posix() + "/")
    return {
        "top_level_file": top_hit_py.exists(),
        "top_level_package": top_hit_pkg is not None,
        "nested_hits": nested_hits[:20],
        "nested_count": len(nested_hits),
    }


def main() -> int:
    print(f"stdlib modules known to interpreter: {len(STDLIB_MODULES)}")

    # Walk the tree
    usage: dict[str, dict] = defaultdict(lambda: {
        "import_statements": [],
        "imported_by_files": set(),
        "aliased_as": set(),
        "uses_attr_access": False,
    })

    parsed = 0
    errors = []
    for py in ROOT.rglob("*.py"):
        if skipped(py.relative_to(ROOT)):
            continue
        try:
            src = py.read_text(errors="replace")
            tree = ast.parse(src, filename=str(py))
        except Exception as e:
            errors.append((py.relative_to(ROOT).as_posix(), f"{type(e).__name__}: {e}"))
            continue
        parsed += 1

        rel = py.relative_to(ROOT).as_posix()
        imports = extract_imports(tree)
        used = used_names(tree)

        for imp in imports:
            top = imp["top"]
            if top not in KNOWN_STDLIB_TOP:
                continue
            info = usage[top]
            info["import_statements"].append({
                "file": rel,
                "lineno": imp["lineno"],
                "form": imp["form"],
                "module": imp["module"],
                "name": imp.get("name"),
                "asname": imp.get("asname"),
                "bound_name": imp["bound_name"],
            })
            info["imported_by_files"].add(rel)
            if imp.get("asname"):
                info["aliased_as"].add(imp["asname"])
            # Did the file reference the top-level name?
            if imp["bound_name"] in used:
                info["uses_attr_access"] = True

    print(f"parsed {parsed} files, {len(errors)} errors")
    print(f"stdlib modules used in tree: {len(usage)}")

    # Compose report
    report = {
        "root": str(ROOT),
        "interpreter_stdlib_count": len(STDLIB_MODULES),
        "parsed_files": parsed,
        "parse_errors": errors,
        "used_modules": {},
        "unused_modules": sorted(KNOWN_STDLIB_TOP - set(usage.keys())),
    }

    for name, info in sorted(usage.items()):
        shadow = classify_shadow(name)
        report["used_modules"][name] = {
            "file_count": len(info["imported_by_files"]),
            "import_statement_count": len(info["import_statements"]),
            "aliases": sorted(info["aliased_as"]),
            "uses_attr_access": info["uses_attr_access"],
            "files": sorted(info["imported_by_files"])[:30],
            "shadow": shadow,
            "sample_imports": info["import_statements"][:10],
        }

    (OUT / "stdlib.json").write_text(json.dumps(report, indent=2, default=list))
    print(f"wrote {OUT / 'stdlib.json'}")

    # Markdown report
    lines = [
        "# Stdlib Mastery Report",
        "",
        f"- Interpreter stdlib modules: **{len(STDLIB_MODULES)}**",
        f"- Parsed files: **{parsed}**",
        f"- Stdlib modules used in tree: **{len(usage)}**",
        f"- Unused: **{len(KNOWN_STDLIB_TOP - set(usage.keys()))}**",
        "",
        "## Used modules, ranked by import count",
        "",
        "| Module | Files | Imports | Aliases | Shadowed? |",
        "|---|---:|---:|---|---|",
    ]

    by_count = sorted(
        usage.items(),
        key=lambda kv: -len(kv[1]["import_statements"]),
    )
    for name, info in by_count:
        shadow = classify_shadow(name)
        shadow_marker = "—"
        if shadow["top_level_file"]:
            shadow_marker = "**yes (top-level file)**"
        elif shadow["top_level_package"]:
            shadow_marker = "**yes (top-level package)**"
        elif shadow["nested_count"]:
            shadow_marker = f"nested ({shadow['nested_count']})"
        aliases = ", ".join(sorted(info["aliased_as"])) or "—"
        lines.append(
            f"| `{name}` | {len(info['imported_by_files'])} | "
            f"{len(info['import_statements'])} | {aliases} | {shadow_marker} |"
        )

    lines.append("")
    lines.append("## Detailed usage")
    lines.append("")

    for name, info in by_count[:40]:
        shadow = classify_shadow(name)
        lines.append(f"### `{name}`")
        lines.append("")
        lines.append(f"- imported in {len(info['imported_by_files'])} files")
        lines.append(f"- {len(info['import_statements'])} import statements")
        if info["aliased_as"]:
            lines.append(f"- aliases: {', '.join(sorted(info['aliased_as']))}")
        if shadow["top_level_file"] or shadow["top_level_package"]:
            lines.append("- **SHADOWED at repo root**")
        if shadow["nested_hits"]:
            lines.append(f"- nested shadow candidates ({shadow['nested_count']}):")
            for h in shadow["nested_hits"][:5]:
                lines.append(f"  - `{h}`")
        lines.append("")
        lines.append("Sample imports:")
        for imp in info["import_statements"][:5]:
            asname = f" as {imp['asname']}" if imp.get("asname") else ""
            if imp["form"] == "import":
                lines.append(f"- `{imp['file']}:{imp['lineno']}` — `import {imp['module']}{asname}`")
            else:
                lines.append(
                    f"- `{imp['file']}:{imp['lineno']}` — "
                    f"`from {imp['module']} import {imp['name']}{asname}`"
                )
        lines.append("")

    lines.append("## Unused stdlib (not imported anywhere)")
    lines.append("")
    unused = sorted(KNOWN_STDLIB_TOP - set(usage.keys()))
    for name in unused:
        lines.append(f"- `{name}`")

    (OUT / "STDLIB.md").write_text("\n".join(lines))
    print(f"wrote {OUT / 'STDLIB.md'}")

    # Summary
    print()
    print("=== summary ===")
    print(f"stdlib modules: {len(STDLIB_MODULES)}")
    print(f"used in tree:  {len(usage)}")
    print(f"unused:        {len(KNOWN_STDLIB_TOP - set(usage.keys()))}")
    print()
    print("top 20 used modules:")
    for name, info in by_count[:20]:
        shadow = classify_shadow(name)
        marker = ""
        if shadow["top_level_file"] or shadow["top_level_package"]:
            marker = "  *** SHADOWED ***"
        elif shadow["nested_count"]:
            marker = f"  (nested shadow x{shadow['nested_count']})"
        print(f"  {name:20s} {len(info['imported_by_files']):4d} files{marker}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
