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
LAYERS = ("ax", "ag", "ac")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def iter_components():
    for layer in LAYERS:
        base = COMPONENTS / layer
        if not base.is_dir():
            continue
        for comp in sorted(base.iterdir()):
            if comp.is_dir():
                yield layer, comp


def pass1_structure() -> dict:
    catalog_state = "missing"
    registered = 0
    if CATALOG.exists():
        try:
            cat = json.loads(CATALOG.read_text())
            catalog_state = "parsed"
            for v in cat.get("layers", {}).values():
                if isinstance(v, list):
                    registered += len(v)
            if registered == 0 and isinstance(cat.get("components"), list):
                registered = len(cat["components"])
        except Exception as e:
            catalog_state = f"parse error: {e}"

    issues = []
    count = 0
    seen = set()
    for layer, comp in iter_components():
        if comp.name in seen:
            continue
        seen.add(comp.name)
        count += 1
        pub = comp / "src" / "public"
        if not pub.is_dir():
            issues.append(f"{layer}/{comp.name}: no src/public/")
            continue
        if not (pub / "__init__.py").exists():
            issues.append(f"{layer}/{comp.name}: no src/public/__init__.py")
        mods = [p for p in pub.glob("*.py") if p.name != "__init__.py"]
        if not mods:
            issues.append(f"{layer}/{comp.name}: no module in src/public/")

    return {
        "catalog": catalog_state,
        "registered": registered,
        "found": count,
        "issues": issues,
    }


def pass2_boilerplate() -> dict:
    hashes = defaultdict(list)
    sizes = []
    for layer, comp in iter_components():
        pub = comp / "src" / "public"
        for mod in pub.glob("*.py"):
            if mod.name == "__init__.py":
                continue
            hashes[sha(mod)].append(f"{layer}/{comp.name}/{mod.name}")
            sizes.append((mod.stat().st_size, f"{layer}/{comp.name}/{mod.name}"))
    dupes = {h: files for h, files in hashes.items() if len(files) > 1}
    sizes.sort()
    return {
        "unique_modules": sum(1 for h, f in hashes.items() if len(f) == 1),
        "duplicate_groups": len(dupes),
        "dupes": dupes,
        "smallest": sizes[:10],
        "largest": sizes[-5:],
    }


def pass3_contracts() -> dict:
    schemas = sorted(CONTRACTS.rglob("*.json")) if CONTRACTS.is_dir() else []
    all_src = "\n".join(
        p.read_text(errors="ignore") for p in COMPONENTS.rglob("*.py")
    )
    unreferenced = []
    ids = {}
    for s in schemas:
        try:
            doc = json.loads(s.read_text())
            sid = doc.get("$id")
            ids[str(s)] = sid
            if sid and sid not in all_src and s.stem not in all_src:
                unreferenced.append(str(s))
        except Exception as e:
            ids[str(s)] = f"PARSE ERROR: {e}"
            unreferenced.append(str(s))
    return {"schemas": len(schemas), "ids": ids, "unreferenced": unreferenced}


def _probe(path: Path, keys: dict) -> dict:
    out = {"present": path.exists()}
    if not path.exists():
        return out
    src = path.read_text(errors="ignore")
    out["lines"] = len(src.splitlines())
    for name, needles in keys.items():
        out[name] = any(n in src for n in needles)
    return out


def pass4_invariants() -> dict:
    return {
        "gov_krn_001": _probe(
            COMPONENTS / "ag" / "GOV-KRN-001-governance-object-model-and-registry"
            / "src" / "public" / "registry.py",
            {
                "version": ("version", "Version", "VERSION"),
                "sqlite": ("sqlite", "SQLite", "sqlite3"),
                "immutable": ("immutab", "Immutable", "IMMUTABLE"),
                "append_only": ("append", "insert", "INSERT"),
                "hash_chain": ("sha256", "hashlib", "digest"),
            },
        ),
        "gov_krn_002": _probe(
            COMPONENTS / "ag" / "GOV-KRN-002-governed-state-and-transition-engine"
            / "src" / "public" / "engine.py",
            {
                "transition": ("transition", "Transition"),
                "worm": ("worm", "WORM"),
                "envelope": ("envelope", "Envelope"),
            },
        ),
        "cmp_evd_001": _probe(
            COMPONENTS / "ac" / "CMP-EVD-001-observation-and-telemetry"
            / "src" / "public" / "telemetry.py",
            {
                "hardware": ("psutil", "platform", "cpu_count", "os."),
                "metrics": ("metrics", "Metrics"),
            },
        ),
        "cog_core_001": _probe(
            COMPONENTS / "ax" / "COG-CORE-001-cognitive-runtime"
            / "src" / "public" / "runtime.py",
            {
                "mlx": ("mlx", "MLX"),
                "prompt": ("prompt", "execute"),
            },
        ),
    }


def main() -> int:
    print("=" * 70)
    print("SPEC AUDIT — Aether Sovereign Fabric")
    print("=" * 70)

    p1 = pass1_structure()
    print("\n[1] STRUCTURE")
    print(f"    catalog state         : {p1['catalog']}")
    print(f"    registered in catalog : {p1['registered']}")
    print(f"    component dirs found  : {p1['found']}")
    print(f"    structural issues     : {len(p1['issues'])}")
    for i in p1["issues"][:30]:
        print(f"      - {i}")

    p2 = pass2_boilerplate()
    print("\n[2] BOILERPLATE")
    print(f"    unique module hashes  : {p2['unique_modules']}")
    print(f"    duplicate groups      : {p2['duplicate_groups']}")
    for h, files in list(p2["dupes"].items())[:10]:
        print(f"      {h[:12]}… shared by {len(files)}:")
        for f in files[:8]:
            print(f"        {f}")
    print("    smallest modules:")
    for size, name in p2["smallest"]:
        print(f"      {size:6d} B  {name}")
    print("    largest modules:")
    for size, name in p2["largest"]:
        print(f"      {size:6d} B  {name}")

    p3 = pass3_contracts()
    print("\n[3] CONTRACTS")
    print(f"    schema files          : {p3['schemas']}")
    print(f"    unreferenced schemas  : {len(p3['unreferenced'])}")
    for u in p3["unreferenced"]:
        print(f"      - {u}")
    for path, sid in p3["ids"].items():
        print(f"      $id {sid!r}  {path}")

    p4 = pass4_invariants()
    print("\n[4] INVARIANT PROBES")
    for comp, res in p4.items():
        print(f"    {comp}: present={res['present']} lines={res.get('lines', 0)}")
        for k, v in res.items():
            if k in ("present", "lines"):
                continue
            print(f"        {k}: {v}")

    print("\n" + "=" * 70)
    failed = (
        p1["catalog"] != "parsed"
        or bool(p1["issues"])
        or p2["duplicate_groups"] > 0
        or bool(p3["unreferenced"])
    )
    print("VERDICT:", "NOT SPEC-CONFORMANT" if failed else "passes structural audit")
    print("=" * 70)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
