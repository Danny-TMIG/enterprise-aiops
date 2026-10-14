#!/usr/bin/env python3
"""spec_audit.py — audit the Aether monorepo against the ASF spec."""
from __future__ import annotations
import hashlib, json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPONENTS = ROOT / "components"
CONTRACTS = ROOT / "contracts"
CATALOG = ROOT / "catalog" / "components.json"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def pass1_structure() -> dict:
    registered = set()
    if CATALOG.exists():
        cat = json.loads(CATALOG.read_text())
        for layer in cat.get("layers", {}).values():
            registered.update(layer if isinstance(layer, list) else [])
    found = {d.name for d in COMPONENTS.rglob("*") if d.is_dir() and d.parent.parent == COMPONENTS}
    missing_impl = []
    for layer in ("ax", "ag", "ac"):
        for comp in (COMPONENTS / layer).iterdir() if (COMPONENTS / layer).exists() else []:
            pub = comp / "src" / "public"
            if not (pub / "__init__.py").exists():
                missing_impl.append(f"{comp.name}: no src/public/__init__.py")
            elif not any(pub.glob("*.py")) or all(p.name == "__init__.py" for p in pub.glob("*.py")):
                missing_impl.append(f"{comp.name}: src/public has no module")
    return {"registered": len(registered), "found": len(found), "issues": missing_impl}

def pass2_boilerplate() -> dict:
    hashes = defaultdict(list)
    for layer in ("ax", "ag", "ac"):
        base = COMPONENTS / layer
        if not base.exists():
            continue
        for comp in base.iterdir():
            pub = comp / "src" / "public"
            for mod in pub.glob("*.py"):
                if mod.name == "__init__.py":
                    continue
                hashes[sha(mod)].append(f"{layer}/{comp.name}/{mod.name}")
    dupes = {h: files for h, files in hashes.items() if len(files) > 1}
    unique = sum(1 for h, files in hashes.items() if len(files) == 1)
    return {"unique_modules": unique, "duplicate_groups": len(dupes), "dupes": dupes}

def pass3_contracts() -> dict:
    schemas = list(CONTRACTS.rglob("*.json")) if CONTRACTS.exists() else []
    schema_ids = {}
    for s in schemas:
        try:
            doc = json.loads(s.read_text())
            schema_ids[s] = doc.get("$id")
        except Exception as e:
            schema_ids[s] = f"PARSE ERROR: {e}"
    unreferenced = []
    all_src = "\n".join(p.read_text(errors="ignore") for p in COMPONENTS.rglob("*.py"))
    for s, sid in schema_ids.items():
        if sid and sid not in all_src and s.stem not in all_src:
            unreferenced.append(str(s))
    return {"schemas": len(schemas), "unreferenced": unreferenced}

def pass4_invariants() -> dict:
    results = {}
    # WORM immutability probe on GOV-KRN-001 if present
    reg = COMPONENTS / "ag" / "GOV-KRN-001-governance-object-model-and-registry" / "src" / "public" / "registry.py"
    results["gov_krn_001_present"] = reg.exists()
    if reg.exists():
        src = reg.read_text()
        results["gov_krn_001_mentions_version"] = "version" in src.lower()
        results["gov_krn_001_mentions_sqlite"] = "sqlite" in src.lower()
        results["gov_krn_001_mentions_immutable"] = "immutab" in src.lower()
    tel = COMPONENTS / "ac" / "CMP-EVD-001-observation-and-telemetry" / "src" / "public" / "telemetry.py"
    results["cmp_evd_001_present"] = tel.exists()
    if tel.exists():
        src = tel.read_text()
        results["cmp_evd_001_reads_hardware"] = any(k in src for k in ("psutil", "platform", "os.cpu_count"))
        results["cmp_evd_001_returns_metrics"] = "metrics" in src.lower()
    return results

def main() -> int:
    print("=" * 70)
    print("SPEC AUDIT — Aether Sovereign Fabric")
    print("=" * 70)
    p1 = pass1_structure()
    print(f"\n[1] STRUCTURE")
    print(f"    registered in catalog : {p1['registered']}")
    print(f"    component dirs found  : {p1['found']}")
    print(f"    structural issues     : {len(p1['issues'])}")
    for i in p1["issues"][:20]:
        print(f"      - {i}")

    p2 = pass2_boilerplate()
    print(f"\n[2] BOILERPLATE")
    print(f"    unique module hashes  : {p2['unique_modules']}")
    print(f"    duplicate groups      : {p2['duplicate_groups']}")
    for h, files in list(p2["dupes"].items())[:10]:
        print(f"      {h[:12]}… shared by {len(files)} files:")
        for f in files[:5]:
            print(f"        {f}")
        if len(files) > 5:
            print(f"        … and {len(files)-5} more")

    p3 = pass3_contracts()
    print(f"\n[3] CONTRACTS")
    print(f"    schema files          : {p3['schemas']}")
    print(f"    unreferenced schemas  : {len(p3['unreferenced'])}")
    for u in p3["unreferenced"][:20]:
        print(f"      - {u}")

    p4 = pass4_invariants()
    print(f"\n[4] INVARIANT PROBES")
    for k, v in p4.items():
        print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    failed = bool(p1["issues"]) or p2["duplicate_groups"] > 0 or bool(p3["unreferenced"])
    print("VERDICT:", "NOT SPEC-CONFORMANT" if failed else "passes structural audit")
    print("=" * 70)
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
