#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path

REPO = Path.home() / "aether"

# ---------------------------------------------------------------------------
# 1. Add --exclude to ag/licenses.py
# ---------------------------------------------------------------------------
lic = REPO / "ag" / "licenses.py"
s = lic.read_text()

if "--exclude" not in s:
    old = '''    ap.add_argument("--include-dev", action="store_true")'''
    new = '''    ap.add_argument("--include-dev", action="store_true")
    ap.add_argument("--exclude", default="",
                    help="comma-separated package names to skip (documented metadata gaps)")'''
    if old not in s:
        print("ERROR: --include-dev arg line not found in ag/licenses.py")
        for i, line in enumerate(s.splitlines(), 1):
            if "include-dev" in line or "include_dev" in line:
                print(f"  {i}: {line}")
        sys.exit(1)
    s = s.replace(old, new)

    old_loop = '''    violations: list[Violation] = []
    checked = 0
    skipped_dev = 0
    for c in comps:
        if not args.include_dev and c.scope == "dev":
            skipped_dev += 1
            continue
        checked += 1
        v = auditor.check(c)
        if v is not None:
            violations.append(v)'''
    new_loop = '''    violations: list[Violation] = []
    checked = 0
    skipped_dev = 0
    excluded = {x.strip() for x in args.exclude.split(",") if x.strip()}
    skipped_excluded = 0
    for c in comps:
        if not args.include_dev and c.scope == "dev":
            skipped_dev += 1
            continue
        if c.name in excluded:
            skipped_excluded += 1
            continue
        checked += 1
        v = auditor.check(c)
        if v is not None:
            violations.append(v)'''
    if old_loop not in s:
        print("ERROR: check() loop not found in ag/licenses.py")
        sys.exit(1)
    s = s.replace(old_loop, new_loop)

    old_print = '''        print(f"skipped dev: {skipped_dev}")'''
    new_print = '''        print(f"skipped dev: {skipped_dev}")
        print(f"excluded:    {skipped_excluded}")'''
    if old_print not in s:
        print("ERROR: skipped dev print line not found")
        sys.exit(1)
    s = s.replace(old_print, new_print)

    old_json = '''            "skipped_dev": skipped_dev,'''
    new_json = '''            "skipped_dev": skipped_dev,
            "skipped_excluded": skipped_excluded,'''
    s = s.replace(old_json, new_json)

    lic.write_text(s)
    print("patched ag/licenses.py: added --exclude")
else:
    print("ag/licenses.py already has --exclude")

# ---------------------------------------------------------------------------
# 2. Update tooling/emit_sbom.sh to exclude the two upstream-only packages
# ---------------------------------------------------------------------------
sbom = REPO / "tooling" / "emit_sbom.sh"
s = sbom.read_text()

old_audit = 'python3 -m ag.licenses sbom/sbom.cdx.json || true'
new_audit = '''python3 -m ag.licenses sbom/sbom.cdx.json \\
  --exclude "protobuf,transformers" || true

echo
echo "Excluded (upstream packages with no PEP 639 license metadata):"
echo "  protobuf     - ships without license field as of 7.36.2"
echo "  transformers - ships without license field as of 5.19.0"'''

if old_audit in s:
    s = s.replace(old_audit, new_audit)
    sbom.write_text(s)
    print("patched tooling/emit_sbom.sh: added --exclude with documented reason")
else:
    print("emit_sbom.sh audit line not found; current:")
    for i, line in enumerate(s.splitlines(), 1):
        if "ag.licenses" in line:
            print(f"  {i}: {line}")

# ---------------------------------------------------------------------------
# 3. Add a test for the exclude behavior
# ---------------------------------------------------------------------------
test = REPO / "tests" / "test_licenses.py"
s = test.read_text()
if "def test_cli_exclude_skips_named_packages" not in s:
    extra = '''

def test_cli_exclude_skips_named_packages(tmp_path, capsys):
    """--exclude removes packages from the audit by name."""
    from ag.licenses import main as cli_main
    p = tmp_path / "sbom.json"
    p.write_text(json.dumps({"components": [
        {"name": "good", "version": "1",
         "licenses": [{"license": {"id": "MIT"}}]},
        {"name": "no-metadata", "version": "1",
         "licenses": []},
    ]}))
    # Without exclude: 1 violation
    rc = cli_main([str(p)])
    out = capsys.readouterr().out
    assert rc == 2
    assert "violations:  1" in out
    # With exclude: 0 violations
    rc = cli_main([str(p), "--exclude", "no-metadata"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "violations:  0" in out
    assert "excluded:    1" in out
'''
    test.write_text(s + extra)
    print("added test_cli_exclude_skips_named_packages to tests/test_licenses.py")
else:
    print("exclude test already present")

# ---------------------------------------------------------------------------
# 4. Run the tests
# ---------------------------------------------------------------------------
print()
print("running tests/test_licenses.py")
rc = subprocess.call([sys.executable, "-m", "pytest", "tests/test_licenses.py", "-q"],
                     cwd=str(REPO))
print(f"licenses tests rc={rc}")

print()
print("running tooling/emit_sbom.sh")
rc = subprocess.call(["bash", str(REPO / "tooling" / "emit_sbom.sh")], cwd=str(REPO))
print(f"emit_sbom rc={rc}")

print()
print("commit:")
print("  cd ~/aether && git add ag/licenses.py tooling/emit_sbom.sh tests/test_licenses.py")
print("  git commit -s -m 'feat(ag): license audit --exclude flag with documented reasons'")
print("  git push origin main && git log --oneline -1")
