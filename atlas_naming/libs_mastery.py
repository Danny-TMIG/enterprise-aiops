#!/usr/bin/env python3
"""Library mastery: every import in the tree, stdlib or third-party.

Scans:
  - all .py files in the tree
  - all installed site-packages in .venv, .lanes/*, and the active interpreter
  - maps every import statement to a resolved package
  - classifies: stdlib | vendored | third-party | local | unresolved
  - cross-references every import against available versions
  - detects duplicates across venvs
  - detects unused declared dependencies in requirements.txt / pyproject.toml

Writes:
  atlas_naming/libs.json     machine-readable
  atlas_naming/LIBS.md       ranked dependency report
  atlas_naming/CONFLICTS.md  version conflicts across venvs
"""

from __future__ import annotations

import ast
import json
import re
import site
import sys
import sysconfig
from collections import defaultdict
from pathlib import Path

ROOT = Path.cwd().resolve()
OUT = ROOT / "atlas_naming"
OUT.mkdir(exist_ok=True)

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".pytest_cache",
    ".eggs",
    "build",
    "dist",
    ".tox",
    ".cache",
    ".codeql-results",
    ".mesh-codeql-db",
    ".snapshots",
    ".delta",
    ".last-backups",
    ".complete-backups",
    ".benchmarks",
    "atlas_naming",
    "_grammar_spec",
    ".moat",
    ".murmur",
    ".agency",
    ".backrooms",
    "node_modules",
    ".next",
}


def skipped(p: Path) -> bool:
    return any(x in SKIP_DIRS for x in p.parts) or any(x.endswith(".egg-info") for x in p.parts)


# ---------------------------------------------------------------------------
# 1. Enumerate stdlib
# ---------------------------------------------------------------------------


def enumerate_stdlib() -> set[str]:
    names = set()
    stdlib_dir = Path(sysconfig.get_paths()["stdlib"])
    for p in stdlib_dir.glob("*.py"):
        if p.stem != "__init__":
            names.add(p.stem)
    for d in stdlib_dir.iterdir():
        if d.is_dir() and not d.name.startswith("_") and (d / "__init__.py").exists():
            names.add(d.name)
    names |= set(sys.builtin_module_names)
    return names


# ---------------------------------------------------------------------------
# 2. Enumerate installed packages across all venvs
# ---------------------------------------------------------------------------


def dist_metadata(pkg_dir: Path) -> dict:
    """Read the metadata from a *.dist-info directory."""
    name = version = summary = ""
    m = pkg_dir.name
    match = re.match(r"(.+?)-([0-9][^-]*)\.dist-info$", m)
    if match:
        name = match.group(1)
        version = match.group(2)
    meta = pkg_dir / "METADATA"
    if meta.exists():
        for line in meta.read_text(errors="replace").splitlines()[:50]:
            if line.startswith("Name:"):
                name = line[5:].strip() or name
            elif line.startswith("Version:"):
                version = line[8:].strip() or version
            elif line.startswith("Summary:"):
                summary = line[8:].strip()
    return {"name": name, "version": version, "summary": summary[:120]}


def enumerate_installed(site_dir: Path) -> dict:
    """Map top-level package name -> metadata for everything installed here."""
    installed = {}
    if not site_dir.exists():
        return installed
    for entry in site_dir.iterdir():
        if entry.name.endswith(".dist-info"):
            info = dist_metadata(entry)
            top_level = info["name"].lower().replace("-", "_")
            installed[top_level] = info
        elif entry.is_dir() and not entry.name.startswith("_"):
            if entry.name.endswith(".egg-info"):
                continue
            top = entry.name
            if top not in installed:
                installed[top] = {"name": top, "version": "?", "summary": ""}
    return installed


def find_venv_site_dirs() -> list[tuple[str, Path]]:
    out = []
    # Active interpreter site-packages
    for p in site.getsitepackages():
        out.append(("current", Path(p)))
    user = site.getusersitepackages()
    if user:
        out.append(("user", Path(user)))
    # Every .venv/ and .lanes/*/ on the machine
    for candidate in ROOT.rglob(".venv"):
        if not candidate.is_dir():
            continue
        for sp in candidate.rglob("site-packages"):
            if sp.is_dir():
                out.append((str(candidate.relative_to(ROOT)), sp))
    lanes = ROOT / ".lanes"
    if lanes.exists():
        for lane in lanes.iterdir():
            if not lane.is_dir():
                continue
            for sp in lane.rglob("site-packages"):
                if sp.is_dir():
                    out.append((f".lanes/{lane.name}", sp))
    return out


# ---------------------------------------------------------------------------
# 3. Walk the tree and collect every import
# ---------------------------------------------------------------------------


def extract_imports(tree: ast.AST) -> list[dict]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                out.append(
                    {
                        "form": "import",
                        "module": alias.name,
                        "top": top,
                        "asname": alias.asname,
                        "lineno": node.lineno,
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                out.append(
                    {
                        "form": "relative",
                        "module": "." * node.level + (node.module or ""),
                        "top": None,
                        "asname": None,
                        "lineno": node.lineno,
                    }
                )
                continue
            top = (node.module or "").split(".")[0]
            out.append(
                {
                    "form": "from",
                    "module": node.module or "",
                    "top": top,
                    "name": None,
                    "asname": None,
                    "lineno": node.lineno,
                }
            )
    return out


# ---------------------------------------------------------------------------
# 4. Classify a top-level import name
# ---------------------------------------------------------------------------


def classify(top: str, stdlib: set[str], installed: dict, local_tops: set[str], venvs: dict) -> str:
    if top is None:
        return "relative"
    if top in local_tops:
        return "local"
    if top in installed:
        return "third-party"
    if top in stdlib:
        return "stdlib"
    return "unresolved"


# ---------------------------------------------------------------------------
# 5. Load declared dependencies
# ---------------------------------------------------------------------------


def parse_requirements(path: Path) -> set[str]:
    names = set()
    if not path.exists():
        return names
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-")):
            continue
        m = re.match(r"([A-Za-z0-9_\-\.]+)", line)
        if m:
            names.add(m.group(1).lower().replace("-", "_"))
    return names


def parse_pyproject(path: Path) -> set[str]:
    names = set()
    if not path.exists():
        return names
    text = path.read_text()
    for m in re.finditer(r'"([A-Za-z0-9_\-\.]+)(?:[<>=!~\[][^"]*)?"', text):
        n = m.group(1).lower().replace("-", "_")
        if n not in {"name", "version", "readme", "license"} and len(n) > 1:
            names.add(n)
    return names


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    stdlib = enumerate_stdlib()
    print(f"stdlib modules: {len(stdlib)}")

    venv_sites = find_venv_site_dirs()
    print(f"venv site dirs found: {len(venv_sites)}")
    venvs = {}
    for label, sp in venv_sites:
        if label in venvs:
            continue
        installed = enumerate_installed(sp)
        if installed:
            venvs[label] = installed
            print(f"  {label:20s} {len(installed):4d} packages  ({sp})")

    # All installed union
    all_installed = {}
    for label, installed in venvs.items():
        for name, info in installed.items():
            if name not in all_installed:
                all_installed[name] = {"versions": {}, "labels": []}
            all_installed[name]["versions"][label] = info["version"]
            all_installed[name]["labels"].append(label)

    print(f"unique third-party packages across venvs: {len(all_installed)}")

    # Local top-level package/module names
    local_tops = set()
    for child in ROOT.iterdir():
        if child.name.startswith(".") or child.name in SKIP_DIRS:
            continue
        if child.is_dir():
            if (child / "__init__.py").exists() or any(child.glob("*.py")):
                local_tops.add(child.name)
        elif child.suffix == ".py":
            local_tops.add(child.stem)
    print(f"local top-level names: {len(local_tops)}")

    # Walk tree
    print("walking tree...")
    imports_by_top: dict[str, dict] = defaultdict(
        lambda: {
            "files": set(),
            "statements": 0,
            "aliases": set(),
        }
    )
    imports_by_category = defaultdict(int)
    unresolved = defaultdict(list)
    parsed = 0
    errors = []

    for py in ROOT.rglob("*.py"):
        if skipped(py.relative_to(ROOT)):
            continue
        try:
            tree = ast.parse(py.read_text(errors="replace"), filename=str(py))
        except Exception as e:
            errors.append((py.relative_to(ROOT).as_posix(), f"{type(e).__name__}: {e}"))
            continue
        parsed += 1
        rel = py.relative_to(ROOT).as_posix()
        for imp in extract_imports(tree):
            top = imp["top"]
            if top is None:
                imports_by_category["relative"] += 1
                continue
            cat = classify(top, stdlib, all_installed, local_tops, venvs)
            imports_by_category[cat] += 1
            entry = imports_by_top[top]
            entry["files"].add(rel)
            entry["statements"] += 1
            if imp.get("asname"):
                entry["aliases"].add(imp["asname"])
            if cat == "unresolved":
                unresolved[top].append((rel, imp["lineno"], imp["module"]))

    print(f"parsed {parsed} files, {len(errors)} parse errors")
    print(f"distinct import roots: {len(imports_by_top)}")

    # Categorize each root
    roots = {}
    for top, info in imports_by_top.items():
        cat = classify(top, stdlib, all_installed, local_tops, venvs)
        version_info = {}
        if top in all_installed:
            version_info = {
                "versions": all_installed[top]["versions"],
                "labels": all_installed[top]["labels"],
                "distinct_versions": sorted(set(all_installed[top]["versions"].values())),
            }
        roots[top] = {
            "category": cat,
            "file_count": len(info["files"]),
            "statement_count": info["statements"],
            "aliases": sorted(info["aliases"]),
            "installed": version_info,
            "sample_files": sorted(info["files"])[:10],
        }

    # Declared vs used
    declared = parse_requirements(ROOT / "requirements.txt")
    declared |= parse_requirements(ROOT / "requirements-dev.txt")
    declared |= parse_pyproject(ROOT / "pyproject.toml")
    used_third_party = {k for k, v in roots.items() if v["category"] == "third-party"}
    declared_unused = sorted(declared - used_third_party)
    used_undeclared = sorted(used_third_party - declared)

    report = {
        "root": str(ROOT),
        "stdlib_count": len(stdlib),
        "parsed_files": parsed,
        "parse_errors": errors[:50],
        "venvs": {label: list(installed.keys()) for label, installed in venvs.items()},
        "unique_installed": len(all_installed),
        "roots": roots,
        "category_counts": dict(imports_by_category),
        "unresolved": {k: v[:10] for k, v in list(unresolved.items())[:50]},
        "declared_unused": declared_unused,
        "used_undeclared": used_undeclared,
        "declared_total": len(declared),
    }
    (OUT / "libs.json").write_text(json.dumps(report, indent=2, default=list))
    print(f"wrote {OUT / 'libs.json'}")

    # -------- LIBS.md --------
    md = [
        "# Library Mastery Report",
        "",
        f"- stdlib modules: **{len(stdlib)}**",
        f"- parsed files: **{parsed}**",
        f"- venvs found: **{len(venvs)}**",
        f"- installed packages across all venvs: **{len(all_installed)}**",
        f"- distinct import roots in tree: **{len(imports_by_top)}**",
        f"- declared in requirements/pyproject: **{len(declared)}**",
        "",
        "## Category counts",
        "",
        "| Category | Import statements |",
        "|---|---:|",
    ]
    for cat, count in sorted(imports_by_category.items(), key=lambda kv: -kv[1]):
        md.append(f"| {cat} | {count} |")

    md += [
        "",
        "## Third-party dependencies (used)",
        "",
        "| Package | Files | Statements | Installed versions | Venvs |",
        "|---|---:|---:|---|---|",
    ]
    for top, info in sorted(roots.items(), key=lambda kv: -kv[1]["file_count"]):
        if info["category"] != "third-party":
            continue
        versions = (
            ", ".join(f"`{v}`" for v in info["installed"].get("distinct_versions", [])) or "?"
        )
        labels = ", ".join(info["installed"].get("labels", [])) or "?"
        md.append(
            f"| `{top}` | {info['file_count']} | {info['statement_count']} | {versions} | {labels} |"
        )

    md += [
        "",
        "## Stdlib dependencies (used)",
        "",
        "| Module | Files | Statements | Aliases |",
        "|---|---:|---:|---|",
    ]
    for top, info in sorted(roots.items(), key=lambda kv: -kv[1]["file_count"]):
        if info["category"] != "stdlib":
            continue
        aliases = ", ".join(info["aliases"]) or "—"
        md.append(f"| `{top}` | {info['file_count']} | {info['statement_count']} | {aliases} |")

    md += ["", "## Local imports", "", "| Name | Files | Statements |", "|---|---:|---:|"]
    for top, info in sorted(roots.items(), key=lambda kv: -kv[1]["file_count"]):
        if info["category"] != "local":
            continue
        md.append(f"| `{top}` | {info['file_count']} | {info['statement_count']} |")

    md += [
        "",
        "## Unresolved imports",
        "",
        "These names are not stdlib, not third-party in any venv, and not local.",
        "They are dead imports, missing dependencies, or typos.",
        "",
    ]
    if unresolved:
        md.append("| Name | Files | First site |")
        md.append("|---|---:|---|")
        for top, sites in sorted(unresolved.items(), key=lambda kv: -len(kv[1]))[:50]:
            first = f"`{sites[0][0]}:{sites[0][1]}` — `{sites[0][2]}`"
            md.append(f"| `{top}` | {len(sites)} | {first} |")
    else:
        md.append("None.")

    md += [
        "",
        "## Declared but unused",
        "",
        "Requirements list these, but no file imports them.",
        "",
    ]
    if declared_unused:
        for name in declared_unused:
            md.append(f"- `{name}`")
    else:
        md.append("None.")

    md += [
        "",
        "## Used but undeclared",
        "",
        "Files import these, but requirements.txt / pyproject.toml do not list them.",
        "",
    ]
    if used_undeclared:
        for name in used_undeclared[:80]:
            md.append(f"- `{name}`")
    else:
        md.append("None.")

    (OUT / "LIBS.md").write_text("\n".join(md))
    print(f"wrote {OUT / 'LIBS.md'}")

    # -------- CONFLICTS.md --------
    conflicts = []
    for name, info in all_installed.items():
        versions = set(info["versions"].values())
        versions.discard("?")
        if len(versions) > 1:
            conflicts.append(
                {
                    "name": name,
                    "versions": info["versions"],
                    "labels": info["labels"],
                }
            )
    conflicts.sort(key=lambda c: c["name"])

    lines = [
        "# Dependency Conflicts Across Venvs",
        "",
        f"Found **{len(conflicts)}** packages with different versions in different venvs.",
        "",
    ]
    if conflicts:
        lines += [
            "| Package | Versions by venv |",
            "|---|---|",
        ]
        for c in conflicts:
            cells = "; ".join(f"`{v}` in `{lbl}`" for lbl, v in sorted(c["versions"].items()))
            lines.append(f"| `{c['name']}` | {cells} |")
    else:
        lines.append("No version conflicts. Every package has the same version across all venvs.")
    (OUT / "CONFLICTS.md").write_text("\n".join(lines))
    print(f"wrote {OUT / 'CONFLICTS.md'}")

    # Summary
    print()
    print("=== summary ===")
    print(f"stdlib modules:      {len(stdlib)}")
    print(f"parsed files:        {parsed}")
    print(f"venvs:               {len(venvs)}")
    print(f"installed packages:  {len(all_installed)}")
    print(f"distinct roots:      {len(imports_by_top)}")
    print()
    print("import categories:")
    for cat, count in sorted(imports_by_category.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:15s} {count:6d} statements")
    print()
    print(f"unresolved roots:    {len(unresolved)}")
    print(f"declared unused:     {len(declared_unused)}")
    print(f"used undeclared:     {len(used_undeclared)}")
    print(f"version conflicts:   {len(conflicts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
