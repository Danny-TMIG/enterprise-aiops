#!/usr/bin/env python3
"""scaffold_packages.py — create the Section 4 package layout in every component.

Driven by catalog/spec_manifest.json. Writes only structure and metadata.
Does not write implementation code.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "catalog" / "spec_manifest.json"
COMPONENTS = ROOT / "components"

REQUIRED_DIRS = [
    "src/public", "src/modules", "src/adapters",
    "tests/unit", "tests/contract", "tests/component", "tests/fixtures",
    "config", "migrations", "docs",
]

DOC_FILES = {
    "docs/design.md": "# Design — {id} {title}\n\nImplementation decisions, invariants, and rationale.\n",
    "docs/state-model.md": "# State Model — {id} {title}\n\nOwned state, transition/transaction model, and versioning.\n",
    "docs/failure-behavior.md": "# Failure Behavior — {id} {title}\n\nFailure classes, containment, recovery, and degraded modes.\n",
    "docs/requirements.md": "# Requirements — {id} {title}\n\nRequirement-to-test traceability.\n",
    "README.md": (
        "# {id} — {title}\n\n"
        "Layer: {layer}\nGroup: {group}\nRelease: {release}\n\n"
        "## Purpose\n\n_TBD._\n\n## Public boundary\n\n_TBD._\n\n"
        "## Owner\n\n_TBD._\n\n## Parent specification\n\n{source}\n\n"
        "## Build / test entrypoints\n\n_TBD after stack selection._\n"
    ),
    "CHANGELOG.md": (
        "# Changelog — {id}\n\n## Unreleased\n\n"
        "- Initial package scaffold from ASF v1.2 repository blueprint.\n"
    ),
}


def component_json(entry: dict, source_docs: list[str]) -> dict:
    return {
        "component_id": entry["id"],
        "title": entry["title"],
        "layer": entry["layer"],
        "group": entry["group"],
        "release": entry["release"],
        "parent_specifications": source_docs,
        "requirements": entry.get("requirements", []),
        "provided_contracts": entry.get("provided_contracts", []),
        "consumed_contracts": entry.get("consumed_contracts", []),
        "state_ownership": "UNDECIDED",
        "dependencies": {
            "build": [], "runtime": [], "authority": [], "state": [],
            "optional_deferred": [],
        },
        "modules": [],
        "deployment_mapping": {"unit": "UNDECIDED", "profile": "UNDECIDED"},
        "open_decisions": entry.get("open_decisions", []),
        "invariants": entry.get("invariants", []),
        "boundary_contracts": entry.get("boundary_contracts", {}),
        "boundary_invariants": entry.get("boundary_invariants", []),
    }


def write_if_absent(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content)
    return True


def main() -> int:
    if not MANIFEST.exists():
        print(f"manifest missing: {MANIFEST}")
        return 2
    doc = json.loads(MANIFEST.read_text())
    entries = doc.get("components", [])
    if not entries:
        print("manifest has no components")
        return 2
    source_docs = doc.get("source", [])
    touched = 0
    for entry in entries:
        base = COMPONENTS / entry["layer"] / entry["id"]
        base.mkdir(parents=True, exist_ok=True)
        for d in REQUIRED_DIRS:
            (base / d).mkdir(parents=True, exist_ok=True)
            keep = base / d / ".gitkeep"
            if not keep.exists() and not any((base / d).iterdir()):
                keep.write_text("")
        public = base / "src" / "public"
        if not (public / "__init__.py").exists():
            (public / "__init__.py").write_text("")
        ctx = {
            "id": entry["id"], "title": entry["title"], "layer": entry["layer"],
            "group": entry["group"], "release": entry["release"],
            "source": ", ".join(source_docs) or "TBD",
        }
        for relpath, template in DOC_FILES.items():
            write_if_absent(base / relpath, template.format(**ctx))
        cj = base / "component.json"
        if not cj.exists():
            cj.write_text(json.dumps(component_json(entry, source_docs), indent=2))
        touched += 1
    print(f"scaffolded packages: {touched}")
    print(f"manifest seal: {doc.get('omega_seal', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
