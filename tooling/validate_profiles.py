#!/usr/bin/env python3
"""validate_profiles.py — assert every profile.json in deploy/profiles/
   (a) parses as JSON,
   (b) has required keys,
   (c) has a unit_map whose values resolve to deploy/units/<id>/unit.json,
   (d) has every unit.json parse and carry required keys.
   Exits non-zero on any failure.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "deploy" / "profiles"
UNITS = ROOT / "deploy" / "units"

PROFILE_REQUIRED = {"profile_id"}
UNIT_REQUIRED = {"unit_id", "owner", "constituent_components"}

def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)

def main() -> int:
    errors: list[str] = []
    profile_count = 0
    unit_ids_seen: set[str] = set()

    for prof in sorted(PROFILES.rglob("*.json")):
        # Only treat files that look like top-level profiles (have profile_id)
        try:
            d = json.loads(prof.read_text())
        except Exception as e:
            fail(f"{prof}: invalid JSON: {e}", errors)
            continue

        if not isinstance(d, dict) or "profile_id" not in d:
            continue  # e.g. federation.json, domain bindings — not a profile
        profile_count += 1

        missing = PROFILE_REQUIRED - d.keys()
        if missing:
            fail(f"{prof}: missing keys {sorted(missing)}", errors)

        unit_map = d.get("unit_map")
        if unit_map is None:
            # profiles without a unit_map are allowed (e.g. m4-max-local)
            continue

        if not isinstance(unit_map, dict):
            fail(f"{prof}: unit_map must be an object", errors)
            continue

        for uid, rel in unit_map.items():
            unit_ids_seen.add(uid)
            upath = ROOT / rel / "unit.json"
            if not upath.exists():
                fail(f"{prof}: unit_map[{uid}] -> {upath} missing", errors)
                continue
            try:
                u = json.loads(upath.read_text())
            except Exception as e:
                fail(f"{upath}: invalid JSON: {e}", errors)
                continue
            umiss = UNIT_REQUIRED - u.keys()
            if umiss:
                fail(f"{upath}: missing keys {sorted(umiss)}", errors)
            if u.get("unit_id") != uid:
                fail(f"{upath}: unit_id mismatch ({u.get('unit_id')!r} != {uid!r})", errors)

        # every node.units[] must reference a unit in unit_map
        for node in d.get("nodes", []):
            for u in node.get("units", []):
                if u not in unit_map:
                    fail(f"{prof}: node {node.get('node_id')} references unit {u!r} not in unit_map", errors)

    print(f"profiles checked    : {profile_count}")
    print(f"unit ids referenced : {len(unit_ids_seen)}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK — all profiles valid and unit_map resolves")
    return 0

if __name__ == "__main__":
    sys.exit(main())
