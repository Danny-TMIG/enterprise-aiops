#!/usr/bin/env python3
"""Aether monorepo structural validator.

Reads catalog/components.json, flattens the layer arrays, and confirms
each registered component has a src/public/__init__.py and at least one
module under src/public/.
"""

from __future__ import annotations

from pathlib import Path as _Path
def _find_repo_root(start=None):
    p = (start or _Path(__file__)).resolve()
    if p.is_file(): p = p.parent
    for parent in [p, *p.parents]:
        if (parent / 'pyproject.toml').exists(): return parent
    return p.parent.parent
_REPO_ROOT = _find_repo_root()

import sys
from pathlib import Path

ROOT = _REPO_ROOT
def _flatten_catalog(doc: dict) -> list[str]:
    if "layers" in doc and isinstance(doc["layers"], dict):
        flat: list[str] = []
        for names in doc["layers"].values():
            flat.extend(names)
        return flat
    return list(doc.get("components", []))


def main() -> int:
    print("🔍 [LINTER] Starting Aether monorepo structural validation...")
    catalog_path = ROOT / "catalog" / "components.json"
    if not catalog_path.exists():
        alt = ROOT / "catalog" / "inventories" / "components.json"
        if alt.exists():
            catalog_path = alt
    if not catalog_path.exists():
        print("❌ CRITICAL: catalog/components.json is missing.")
        return 1

    import json

    catalog_data = json.loads(catalog_path.read_text())
    components = _flatten_catalog(catalog_data)
    print(f"  ✔ Loaded catalog containing {len(components)} registered components.")

    issues: list[str] = []
    for comp in components:
        found = None
        for layer in ("ax", "ag", "ac"):
            cand = ROOT / "components" / layer / comp
            if cand.is_dir():
                found = cand
                break
        if found is None:
            issues.append(f"{comp}: directory not found")
            continue
        pub = found / "src" / "public"
        if not pub.is_dir():
            issues.append(f"{comp}: no src/public/")
            continue
        if not (pub / "__init__.py").exists():
            issues.append(f"{comp}: no src/public/__init__.py")
        mods = [p for p in pub.glob("*.py") if p.name != "__init__.py"]
        if not mods:
            issues.append(f"{comp}: no module in src/public/")

    print()
    print("-" * 50)
    print(f"Validation Complete: {len(components)} components checked.")
    print(f"Errors: {len(issues)} | Warnings: 0")
    for i in issues[:20]:
        print(f"  - {i}")
    print("-" * 50)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
