#!/usr/bin/env python3
"""validate_frontend.py — structural check on the generated frontend.

Verifies:
  * every manifest component has a real .ts and a real .test.ts
  * every manifest page exists
  * package.json, tsconfig.json, vite.config.ts, vitest.config.ts exist
  * no generated file is empty and none contains obvious stub markers
  * the manifest declares at least one honestly-unavailable capability
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "catalog" / "frontend_manifest.json"
TARGET = ROOT / "public"

STUB_MARKERS = ("TODO", "FIXME", "not implemented", "placeholder")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    errors: list[str] = []

    for comp in manifest["components"]:
        t = TARGET / "src" / "components" / f"{comp}.ts"
        u = ROOT / "tests" / "unit" / f"{comp}.test.ts"
        if not t.exists():
            errors.append(f"missing component: {t.relative_to(ROOT)}")
        if not u.exists():
            errors.append(f"missing unit test: {u.relative_to(ROOT)}")

    for page in manifest["pages"]:
        p = TARGET / f"{page}.html"
        if not p.exists():
            errors.append(f"missing page: {p.relative_to(ROOT)}")

    for f in ["package.json", "tsconfig.json", "vite.config.ts", "vitest.config.ts"]:
        if not (ROOT / f).exists():
            errors.append(f"missing build file: {f}")

    for p in list(TARGET.rglob("*.ts")) + list(TARGET.rglob("*.css")) + list(TARGET.rglob("*.html")):
        src = p.read_text(errors="ignore")
        if not src.strip():
            errors.append(f"empty file: {p.relative_to(ROOT)}")
            continue
        low = src.lower()
        for m in STUB_MARKERS:
            if m.lower() in low:
                errors.append(f"stub marker {m!r} in {p.relative_to(ROOT)}")
                break

    if not manifest.get("declared_unavailable"):
        errors.append("manifest.declared_unavailable is empty — anti-stub rule requires honesty about gaps")

    if errors:
        print(f"validate_frontend: {len(errors)} error(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("validate_frontend: OK — no missing pieces, no stubs, gaps declared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
