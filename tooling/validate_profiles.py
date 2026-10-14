#!/usr/bin/env python3
"""validate_profiles.py — schema + cross-reference validator.

Checks:
  P1  profile.json parses and matches profile.schema.json
  P2  profile_id unique
  P3  every unit_map value resolves to a real unit.json
  P4  every node.units[] entry appears in unit_map
  P5  every node.unit_id appears in unit_map
  U1  unit.json parses and matches unit.schema.json
  U2  unit_id matches directory name
  U3  every constituent_component has a real src/public/ module
  U4  every state_owner is also a constituent_component
  U5  every dependency resolves to a known unit
  U6  placement matches an existing profile
  U7  runbook.md exists and mentions every dependency
  U8  every profile_binding points to a profile that lists this unit
  X1  no orphan unit directory
  X2  no duplicate unit_id
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "deploy" / "profiles"
UNITS = ROOT / "deploy" / "units"
COMPONENTS = ROOT / "components"

PROFILE_SCHEMA = PROFILES / "profile.schema.json"
UNIT_SCHEMA = UNITS / "unit.schema.json"
COMPONENT_ID_RE = re.compile(r"^([A-Z]{3}-[A-Z]{3}-[0-9]{3})-")


def _load(path: Path):
    if not path.exists():
        print(f"FATAL: missing schema {path}", file=sys.stderr)
        sys.exit(2)
    return json.loads(path.read_text())


def _min_schema(schema: dict, obj, path: str, errs: list[str]) -> None:
    t = schema.get("type")
    if t == "object":
        if not isinstance(obj, dict):
            errs.append(f"{path}: expected object"); return
        for k in schema.get("required", []):
            if k not in obj:
                errs.append(f"{path}: missing {k!r}")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            for k in obj:
                if k not in allowed:
                    errs.append(f"{path}: unexpected key {k!r}")
        for k, v in obj.items():
            if k in schema.get("properties", {}):
                _min_schema(schema["properties"][k], v, f"{path}.{k}", errs)
    elif t == "array":
        if not isinstance(obj, list):
            errs.append(f"{path}: expected array"); return
        if "minItems" in schema and len(obj) < schema["minItems"]:
            errs.append(f"{path}: needs >= {schema['minItems']} items")
        if "items" in schema:
            for i, it in enumerate(obj):
                _min_schema(schema["items"], it, f"{path}[{i}]", errs)
    elif t == "string":
        if not isinstance(obj, str):
            errs.append(f"{path}: expected string"); return
        if "minLength" in schema and len(obj) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(obj) > schema["maxLength"]:
            errs.append(f"{path}: longer than {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], obj):
            errs.append(f"{path}: {obj!r} fails pattern {schema['pattern']!r}")
        if "enum" in schema and obj not in schema["enum"]:
            errs.append(f"{path}: {obj!r} not in {schema['enum']}")
    elif t == "number":
        if not isinstance(obj, (int, float)) or isinstance(obj, bool):
            errs.append(f"{path}: expected number"); return
        if "exclusiveMinimum" in schema and obj <= schema["exclusiveMinimum"]:
            errs.append(f"{path}: must be > {schema['exclusiveMinimum']}")
    elif isinstance(t, list):
        ok = False
        for sub in t:
            if sub == "null" and obj is None: ok = True; break
            if sub == "string" and isinstance(obj, str): ok = True; break
            if sub == "number" and isinstance(obj, (int, float)) and not isinstance(obj, bool): ok = True; break
        if not ok:
            errs.append(f"{path}: type not in {t}")


def _component_exists(cid: str) -> bool:
    m = COMPONENT_ID_RE.match(cid)
    if not m:
        return False
    prefix = m.group(1)
    for layer in ("ax", "ag", "ac"):
        base = COMPONENTS / layer
        if not base.is_dir():
            continue
        for d in base.iterdir():
            if d.name.startswith(prefix):
                pub = d / "src" / "public"
                if pub.is_dir() and any(p.name != "__init__.py" for p in pub.glob("*.py")):
                    return True
    return False


def main() -> int:
    errors: list[str] = []
    unit_schema = _load(UNIT_SCHEMA)
    profile_schema = _load(PROFILE_SCHEMA)

    profiles: dict[str, dict] = {}
    profile_paths: dict[str, Path] = {}
    for prof in sorted(PROFILES.rglob("profile.json")):
        try:
            d = json.loads(prof.read_text())
        except Exception as e:
            errors.append(f"{prof}: invalid JSON: {e}"); continue
        _min_schema(profile_schema, d, str(prof.relative_to(ROOT)), errors)
        pid = d.get("profile_id")
        if pid:
            if pid in profiles:
                errors.append(f"{prof}: duplicate profile_id {pid!r}")
            profiles[pid] = d
            profile_paths[pid] = prof

    units: dict[str, dict] = {}
    unit_paths: dict[str, Path] = {}
    if UNITS.is_dir():
        for ufile in sorted(UNITS.glob("*/unit.json")):
            try:
                u = json.loads(ufile.read_text())
            except Exception as e:
                errors.append(f"{ufile}: invalid JSON: {e}"); continue
            _min_schema(unit_schema, u, str(ufile.relative_to(ROOT)), errors)
            uid = u.get("unit_id")
            if not uid:
                continue
            if uid in units:
                errors.append(f"{ufile}: duplicate unit_id {uid!r}")
            units[uid] = u
            unit_paths[uid] = ufile

            if uid != ufile.parent.name:
                errors.append(f"{ufile}: unit_id {uid!r} != dir {ufile.parent.name!r}")

            for cid in u.get("constituent_components", []):
                if not _component_exists(cid):
                    errors.append(f"{ufile}: component {cid!r} has no real src/public/ module")

            cons = set(u.get("constituent_components", []))
            for so in u.get("state_owners", []):
                if so not in cons:
                    errors.append(f"{ufile}: state_owner {so!r} not in constituent_components")

            placement = u.get("placement", "")
            if placement and placement not in profiles:
                errors.append(f"{ufile}: placement {placement!r} has no matching profile")

            runbook = ufile.parent / "runbook.md"
            if not runbook.exists() or len(runbook.read_text().strip()) < 40:
                errors.append(f"{ufile}: runbook.md missing or too short")
            else:
                rb = runbook.read_text()
                for dep in u.get("dependencies", []):
                    if dep not in rb:
                        errors.append(f"{ufile}: runbook does not mention dependency {dep!r}")

    referenced: set[str] = set()
    for pid, prof in profiles.items():
        umap = prof.get("unit_map", {})
        for uid, rel in umap.items():
            referenced.add(uid)
            if not (ROOT / rel / "unit.json").exists():
                errors.append(f"{profile_paths[pid]}: unit_map[{uid!r}] -> missing unit.json")
        for node in prof.get("nodes", []):
            for u in node.get("units", []):
                if umap and u not in umap:
                    errors.append(f"{profile_paths[pid]}: node {node.get('node_id')} refs {u!r} not in unit_map")
            nid = node.get("unit_id")
            if nid and umap and nid not in umap:
                errors.append(f"{profile_paths[pid]}: node {node.get('node_id')} unit_id {nid!r} not in unit_map")

    for uid, u in units.items():
        for dep in u.get("dependencies", []):
            if dep not in units:
                errors.append(f"{unit_paths[uid]}: dependency {dep!r} unknown")
        for pbid in u.get("profile_bindings", []):
            p = profiles.get(pbid)
            if not p:
                errors.append(f"{unit_paths[uid]}: profile_binding {pbid!r} has no profile"); continue
            if uid not in (p.get("unit_map") or {}):
                errors.append(f"{unit_paths[uid]}: profile {pbid!r} does not list unit in unit_map")

    if UNITS.is_dir():
        for d in sorted(UNITS.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            if (d / "unit.json").exists() and d.name not in referenced:
                errors.append(f"{d}: orphan unit not referenced by any profile")

    print(f"profiles checked : {len(profiles)}")
    print(f"units checked    : {len(units)}")
    print(f"units referenced : {len(referenced)}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK — schema-valid, cross-referenced, orphan-free")
    return 0


if __name__ == "__main__":
    sys.exit(main())
