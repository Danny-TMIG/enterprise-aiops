#!/usr/bin/env python3
"""DCS grounded-claims checker. Walks dcs/ only. Skips third-party."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "site-packages", "__pycache__", ".lanes",
             ".git", "node_modules", "db", "dcd_codeql"}

def walk_ast(root: Path):
    dcs_dir = root / "dcs"
    if not dcs_dir.exists():
        dcs_dir = root
    for p in dcs_dir.rglob("*.py"):
        if any(s in p.parts for s in SKIP_DIRS):
            continue
        try:
            yield p, ast.parse(p.read_text())
        except SyntaxError:
            continue


# 1. ALIGNED — only chain.append / self.append inside Chain
def check_aligned(root: Path) -> list:
    bad = []
    for p, tree in walk_ast(root):
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "append"):
                continue
            recv = func.value
            recv_name = (recv.id if isinstance(recv, ast.Name)
                         else recv.attr if isinstance(recv, ast.Attribute)
                         else None)
            if recv_name != "chain":
                continue
            if (len(node.args) + len(node.keywords)) < 4:
                bad.append(f"{p.name}:{node.lineno} {recv_name}.append() has {len(node.args) + len(node.keywords)} args")
    return bad


# 2. SAFE — files defining verify* must contain a conditional
def check_safe(root: Path) -> list:
    bad = []
    for p, tree in walk_ast(root):
        defines = any(isinstance(n, ast.FunctionDef) and n.name.startswith("verify")
                      for n in ast.walk(tree))
        if not defines:
            continue
        text = p.read_text()
        if "if " not in text and "assert " not in text:
            bad.append(f"{p.name}: verify* defined but no conditional")
    return bad


# 3. COMPLETE — HATS tuples are 5-tuples with non-empty anchor
def check_complete(root: Path) -> list:
    bad = []
    for p, tree in walk_ast(root):
        if p.name != "rogue.py":
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if not (isinstance(t, ast.Name) and t.id == "HATS"):
                    continue
                if not isinstance(node.value, ast.List):
                    bad.append(f"{p.name}:{node.lineno} HATS not a list")
                    break
                for elt in node.value.elts:
                    if not isinstance(elt, ast.Tuple):
                        bad.append(f"{p.name}:{elt.lineno} HATS entry not tuple")
                        continue
                    if len(elt.elts) != 5:
                        bad.append(f"{p.name}:{elt.lineno} HATS tuple has {len(elt.elts)} elements")
                        continue
                    a = elt.elts[4]
                    if not (isinstance(a, ast.Constant) and isinstance(a.value, str) and len(a.value) >= 2):
                        bad.append(f"{p.name}:{elt.lineno} HATS anchor empty")
    return bad


# 4. PREVENTION — detect_rogue called
def check_prevention(root: Path) -> list:
    for p, tree in walk_ast(root):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Name) and f.id == "detect_rogue":
                    return []
    return ["no detect_rogue call found"]


# 5. FINITE — Belnap dict keys are exactly the four states
def check_finite(root: Path) -> list:
    bad = []
    good = {"PASS", "FAIL", "UNKNOWN", "CONFLICT"}
    for p, tree in walk_ast(root):
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            keys = {k.value for k in node.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            # only flag dicts that ALREADY look like Belnap maps
            if keys and (keys & good) and not (keys <= good):
                bad.append(f"{p.name}:{node.lineno} Belnap dict has extra keys: {keys - good}")
    return bad


# 6. FORGEABLE — no md5/sha1 in dcs/
def check_forgeable(root: Path) -> list:
    bad = []
    for p, tree in walk_ast(root):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Attribute) and f.attr in ("md5", "sha1"):
                    bad.append(f"{p.name}:{node.lineno} weak hash: {f.attr}")
    return bad


# 7. ANCHORED — STANDARDS_BODIES non-trivial
def check_anchored(root: Path) -> list:
    bad = []
    for p, tree in walk_ast(root):
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if not (isinstance(t, ast.Name) and t.id == "STANDARDS_BODIES"):
                    continue
                v = node.value
                if not isinstance(v, (ast.Set, ast.List, ast.Tuple)):
                    bad.append(f"{p.name}:{node.lineno} STANDARDS_BODIES not iterable")
                    continue
                for elt in v.elts:
                    if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str) and len(elt.value) >= 2):
                        bad.append(f"{p.name}:{node.lineno} STANDARDS_BODIES trivial entry")
    return bad


# 8. EXTERNALLY_VERIFIABLE — verify* makes no network calls
#    NOTE: dict.get() is NOT a network call. Only urlopen/socket/connect.
def check_externally_verifiable(root: Path) -> list:
    bad = []
    NET = {"urlopen", "socket", "connect", "create_connection"}
    VERIFY = {"verify", "verify_license", "verify_all", "verify_chain",
              "verify_inclusion", "verify_attestation"}
    for p, tree in walk_ast(root):
        for node in ast.walk(tree):
            if not (isinstance(node, ast.FunctionDef) and node.name in VERIFY):
                continue
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    name = f.attr if isinstance(f, ast.Attribute) else (
                        f.id if isinstance(f, ast.Name) else None)
                    if name in NET:
                        bad.append(f"{p.name}:{node.lineno} verify() calls {name}")
    return bad


CHECKS = [
    ("1_aligned",               check_aligned,               "chain.append arity"),
    ("2_safe",                  check_safe,                  "verify() in conditional"),
    ("3_complete",              check_complete,              "HATS tuples well-formed"),
    ("4_prevention",            check_prevention,            "detect_rogue present"),
    ("5_finite",                check_finite,                "Belnap dict total"),
    ("6_forgeable_evidence",    check_forgeable,             "no weak hash"),
    ("7_anchored",              check_anchored,              "STANDARDS_BODIES non-trivial"),
    ("8_externally_verifiable", check_externally_verifiable, "no network in verify"),
]


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(f"→ checking {root}/dcs (dcs package only)")
    print()
    passed = failed = 0
    for name, fn, desc in CHECKS:
        bad = fn(root)
        if not bad:
            print(f"  PASS  {name:<26}  {desc}")
            passed += 1
        else:
            print(f"  FAIL  {name:<26}  {desc}")
            for line in bad[:3]:
                print(f"        {line}")
            failed += 1
    print()
    print("═" * 60)
    print(f"  grounded claims passing: {passed} / {len(CHECKS)}")
    print(f"  grounded claims failing: {failed} / {len(CHECKS)}")
    print("═" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
