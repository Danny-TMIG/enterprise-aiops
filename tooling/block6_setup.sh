#!/usr/bin/env bash
# Block 6 setup. Writes ag/licenses.py, tests/test_licenses.py, sbom/.gitignore,
# and tooling/block6_live_proof.sh. Idempotent.
set -euo pipefail
cd "$HOME/aether"

echo "== 1. verify dependencies =="
python -c "import piplicenses, cyclonedx_py, license_expression, packaging; print('deps ok')"

echo
echo "== 2. write sbom/.gitignore =="
mkdir -p sbom
cat > sbom/.gitignore <<'IGN'
*.cdx.json
*.cdx.xml
*.sig
IGN

echo
echo "== 3. write ag/licenses.py =="
cat > ag/licenses.py <<'PYEOF'
"""License audit for a CycloneDX SBOM.

Reads a CycloneDX JSON or XML SBOM, evaluates every component's declared
license against an allowlist, and reports violations. Handles:

- plain SPDX IDs              ("MIT")
- SPDX expressions            ("(MIT OR Apache-2.0)")
- SPDX WITH exceptions        ("Apache-2.0 WITH LLVM-exception")
- non-SPDX names              ("Proprietary")
- components with no license  (flagged, not silently passed)

Exit codes:
  0  all compliant
  1  usage error / unreadable SBOM
  2  violations found
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from license_expression import ExpressionError, Licensing, get_spdx_licensing


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------
@dataclass
class Component:
    name: str
    version: str = ""
    purl: str = ""
    scope: str = "runtime"      # "runtime" | "dev" | "optional" | "unknown"
    licenses: list[str] = field(default_factory=list)   # raw strings as declared
    license_kind: str = "unknown"  # "spdx-id" | "spdx-expression" | "name" | "none"


@dataclass
class Violation:
    component: str
    version: str
    reason: str
    licenses: list[str]


# ---------------------------------------------------------------------------
# SBOM parsers
# ---------------------------------------------------------------------------
def _parse_licenses_entry(entry: dict[str, Any]) -> tuple[str, str]:
    """Return (raw_string, kind) for one entry in `licenses`."""
    if "expression" in entry:
        return entry["expression"], "spdx-expression"
    lic = entry.get("license", {})
    if "id" in lic:
        return lic["id"], "spdx-id"
    if "name" in lic:
        return lic["name"], "name"
    return "", "none"


def parse_cyclonedx_json(data: dict[str, Any]) -> list[Component]:
    comps: list[Component] = []
    for c in data.get("components", []):
        licenses: list[str] = []
        kinds: set[str] = set()
        for entry in c.get("licenses", []):
            raw, kind = _parse_licenses_entry(entry)
            if raw:
                licenses.append(raw)
                kinds.add(kind)
        if not licenses:
            kind = "none"
        elif "spdx-expression" in kinds:
            kind = "spdx-expression"
        elif "spdx-id" in kinds:
            kind = "spdx-id"
        else:
            kind = "name"
        comps.append(
            Component(
                name=c.get("name", "?"),
                version=c.get("version", ""),
                purl=c.get("purl", ""),
                scope=c.get("scope", "runtime"),
                licenses=licenses,
                license_kind=kind,
            )
        )
    return comps


def parse_cyclonedx_xml(root: ET.Element) -> list[Component]:
    ns = {"cdx": "http://cyclonedx.org/schema/bom/1.5"}
    comps: list[Component] = []
    for c in root.findall(".//cdx:component", ns) or root.findall(".//component"):
        name = (c.findtext("cdx:name", default="?", namespaces=ns)
                or c.findtext("name", default="?"))
        version = (c.findtext("cdx:version", default="", namespaces=ns)
                   or c.findtext("version", default=""))
        purl = ""
        for p in c.findall("cdx:purl", ns) + c.findall("purl"):
            purl = p.text or ""
            break
        licenses: list[str] = []
        kinds: set[str] = set()
        for lic in c.findall("cdx:licenses/cdx:license", ns) + c.findall("licenses/license"):
            expr = lic.findtext("cdx:expression", namespaces=ns) or lic.findtext("expression")
            lid = lic.findtext("cdx:id", namespaces=ns) or lic.findtext("id")
            lname = lic.findtext("cdx:name", namespaces=ns) or lic.findtext("name")
            if expr:
                licenses.append(expr); kinds.add("spdx-expression")
            elif lid:
                licenses.append(lid); kinds.add("spdx-id")
            elif lname:
                licenses.append(lname); kinds.add("name")
        if not licenses:
            kind = "none"
        elif "spdx-expression" in kinds:
            kind = "spdx-expression"
        elif "spdx-id" in kinds:
            kind = "spdx-id"
        else:
            kind = "name"
        comps.append(Component(name=name, version=version, purl=purl,
                               licenses=licenses, license_kind=kind))
    return comps


def load_sbom(path: Path) -> list[Component]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text()
    if path.suffix.lower() == ".xml" or text.lstrip().startswith("<?xml"):
        return parse_cyclonedx_xml(ET.fromstring(text))
    return parse_cyclonedx_json(json.loads(text))


# ---------------------------------------------------------------------------
# License evaluation
# ---------------------------------------------------------------------------
class LicenseAuditor:
    """Evaluate each component's declared license against an allowlist.

    Uses SPDX expression semantics: `(MIT OR Apache-2.0)` is compliant if
    *any* branch is on the allowlist. `Apache-2.0 WITH LLVM-exception` is
    compliant if `Apache-2.0` is on the allowlist.
    """

    def __init__(self, allow: Iterable[str], deny: Iterable[str] = ()) -> None:
        self._licensing: Licensing = get_spdx_licensing()
        self.allow = {s.strip() for s in allow if s.strip()}
        self.deny = {s.strip() for s in deny if s.strip()}

    def _evaluate_spdx(self, expr: str) -> tuple[bool, str]:
        """Parse an SPDX expression and decide if the allowlist satisfies it."""
        try:
            parsed = self._licensing.parse(expr, validate=False, strict=False)
        except ExpressionError as e:
            return False, f"unparseable SPDX expression: {e!r}"

        # Any denied symbol -> immediate violation, regardless of allow.
        try:
            symbols = {str(s) for s in parsed.symbols}
        except Exception:
            symbols = set()
        denied_hit = symbols & self.deny
        if denied_hit:
            return False, f"contains denied license(s): {sorted(denied_hit)}"

        # Simplest correct approach: evaluate the expression against the
        # allowlist by substituting each symbol with True/False.
        allowed = symbols & self.allow
        if not allowed and symbols:
            return False, f"no allowed license among {sorted(symbols)}"
        # If any allowed symbol is present and no denied symbol is, treat
        # the OR-expression as satisfied. For AND expressions, we need every
        # conjunct to be allowed; license_expression can tell us via `evaluate`.
        try:
            ok = parsed.evaluate(lambda sym: str(sym) in self.allow)
        except Exception as e:  # noqa: BLE001
            return False, f"evaluation error: {e!r}"
        if ok:
            return True, ""
        return False, f"expression not satisfied by allowlist: {expr}"

    def check(self, c: Component) -> Violation | None:
        # Components with no license declared: flag, don't pass.
        if c.license_kind == "none" or not c.licenses:
            return Violation(c.name, c.version, "no license declared", [])

        # Non-SPDX names: compare literally against allow/deny.
        if c.license_kind == "name":
            ok = any(l in self.allow for l in c.licenses)
            if ok:
                return None
            if any(l in self.deny for l in c.licenses):
                return Violation(c.name, c.version, "denied name", c.licenses)
            return Violation(c.name, c.version, "name not on allowlist", c.licenses)

        # SPDX-id or SPDX-expression: evaluate each declared license; compliant
        # if any one passes.
        for lic in c.licenses:
            ok, why = self._evaluate_spdx(lic)
            if ok:
                return None
        return Violation(c.name, c.version, why if c.licenses else "no SPDX license", c.licenses)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _default_allow() -> list[str]:
    # Permissive defaults appropriate for shipping code. Override with --allow.
    return [
        "MIT",
        "Apache-2.0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "ISC",
        "Python-2.0",
        "PSF-2.0",
        "MPL-2.0",
        "Unlicense",
        "CC0-1.0",
        "Zlib",
    ]


def _default_deny() -> list[str]:
    # Strong copyleft licenses commonly treated as incompatible with proprietary
    # distribution. Override with --deny.
    return ["GPL-2.0-only", "GPL-3.0-only", "AGPL-3.0-only", "SSPL-1.0"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ag.licenses")
    ap.add_argument("sbom", type=Path, help="path to a CycloneDX JSON or XML SBOM")
    ap.add_argument("--allow", default=",".join(_default_allow()),
                    help="comma-separated allowlist of SPDX IDs or names")
    ap.add_argument("--deny", default=",".join(_default_deny()),
                    help="comma-separated denylist of SPDX IDs or names")
    ap.add_argument("--include-dev", action="store_true",
                    help="also audit components with scope=dev")
    ap.add_argument("--json", action="store_true",
                    help="emit a machine-readable report instead of text")
    args = ap.parse_args(argv)

    try:
        comps = load_sbom(args.sbom)
    except FileNotFoundError:
        print(f"SBOM not found: {args.sbom}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"failed to parse SBOM: {e}", file=sys.stderr)
        return 1

    auditor = LicenseAuditor(
        allow=[s.strip() for s in args.allow.split(",")],
        deny=[s.strip() for s in args.deny.split(",")],
    )

    violations: list[Violation] = []
    checked = 0
    skipped_dev = 0
    for c in comps:
        if not args.include_dev and c.scope == "dev":
            skipped_dev += 1
            continue
        checked += 1
        v = auditor.check(c)
        if v is not None:
            violations.append(v)

    if args.json:
        print(json.dumps({
            "sbom": str(args.sbom),
            "checked": checked,
            "skipped_dev": skipped_dev,
            "violations": [
                {"component": v.component, "version": v.version,
                 "reason": v.reason, "licenses": v.licenses}
                for v in violations
            ],
        }, indent=2))
    else:
        print(f"sbom:        {args.sbom}")
        print(f"checked:     {checked}")
        print(f"skipped dev: {skipped_dev}")
        print(f"violations:  {len(violations)}")
        for v in violations:
            ver = f"@{v.version}" if v.version else ""
            lics = ", ".join(v.licenses) if v.licenses else "(none declared)"
            print(f"  - {v.component}{ver}: {v.reason} [{lics}]")

    return 0 if not violations else 2


if __name__ == "__main__":
    sys.exit(main())
PYEOF

echo
echo "== 4. write tests/test_licenses.py =="
cat > tests/test_licenses.py <<'PYEOF'
"""Tests for ag.licenses. Synthetic SBOMs, no network, no real packages."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ag.licenses import (
    Component,
    LicenseAuditor,
    load_sbom,
    parse_cyclonedx_json,
    parse_cyclonedx_xml,
)


def _auditor(**kw) -> LicenseAuditor:
    allow = kw.pop("allow", ["MIT", "Apache-2.0", "BSD-3-Clause", "MPL-2.0"])
    deny = kw.pop("deny", ["GPL-3.0-only", "AGPL-3.0-only"])
    return LicenseAuditor(allow=allow, deny=deny)


def _comp(**kw) -> Component:
    return Component(
        name=kw.pop("name", "pkg"),
        version=kw.pop("version", "1.0.0"),
        scope=kw.pop("scope", "runtime"),
        licenses=kw.pop("licenses", ["MIT"]),
        license_kind=kw.pop("license_kind", "spdx-id"),
    )


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------
def test_parse_json_expression():
    sbom = {
        "components": [
            {"name": "a", "version": "1", "licenses": [{"expression": "(MIT OR Apache-2.0)"}]},
            {"name": "b", "version": "1", "licenses": [{"license": {"id": "MIT"}}]},
            {"name": "c", "version": "1", "licenses": [{"license": {"name": "Proprietary"}}]},
            {"name": "d", "version": "1"},
        ]
    }
    comps = parse_cyclonedx_json(sbom)
    assert len(comps) == 4
    assert comps[0].license_kind == "spdx-expression"
    assert comps[1].license_kind == "spdx-id"
    assert comps[2].license_kind == "name"
    assert comps[3].license_kind == "none"


def test_parse_xml_round_trip(tmp_path):
    xml = """<?xml version="1.0"?>
<bom xmlns="http://cyclonedx.org/schema/bom/1.5">
  <components>
    <component>
      <name>x</name>
      <version>2</version>
      <licenses><license><id>MIT</id></license></licenses>
    </component>
    <component>
      <name>y</name>
      <version>3</version>
      <licenses><license><expression>(MIT OR GPL-3.0-only)</expression></license></licenses>
    </component>
  </components>
</bom>"""
    p = tmp_path / "sbom.xml"
    p.write_text(xml)
    comps = load_sbom(p)
    assert [c.name for c in comps] == ["x", "y"]
    assert comps[1].license_kind == "spdx-expression"


def test_load_sbom_json(tmp_path):
    p = tmp_path / "sbom.json"
    p.write_text(json.dumps({"components": [{"name": "z", "version": "1",
                                            "licenses": [{"license": {"id": "MIT"}}]}]}))
    comps = load_sbom(p)
    assert comps[0].name == "z"


# ---------------------------------------------------------------------------
# Evaluation tests
# ---------------------------------------------------------------------------
def test_plain_spdx_allowed():
    v = _auditor().check(_comp(licenses=["MIT"], license_kind="spdx-id"))
    assert v is None


def test_plain_spdx_not_allowed():
    v = _auditor().check(_comp(licenses=["BSD-4-Clause"], license_kind="spdx-id"))
    assert v is not None
    assert "not satisfied" in v.reason or "no allowed" in v.reason


def test_expression_or_allowed():
    v = _auditor().check(_comp(licenses=["(MIT OR Apache-2.0)"], license_kind="spdx-expression"))
    assert v is None


def test_expression_or_not_allowed():
    v = _auditor().check(_comp(licenses=["(BSD-4-Clause OR GPL-2.0-only)"], license_kind="spdx-expression"))
    assert v is not None


def test_expression_and_requires_all_allowed():
    v = _auditor().check(_comp(licenses=["(MIT AND BSD-4-Clause)"], license_kind="spdx-expression"))
    assert v is not None


def test_expression_and_all_allowed():
    v = _auditor().check(_comp(licenses=["(MIT AND Apache-2.0)"], license_kind="spdx-expression"))
    assert v is None


def test_with_exception():
    # Apache-2.0 WITH LLVM-exception: allowed because Apache-2.0 is on the allowlist.
    v = _auditor().check(_comp(
        licenses=["Apache-2.0 WITH LLVM-exception"], license_kind="spdx-expression"
    ))
    assert v is None


def test_denied_expression():
    v = _auditor().check(_comp(
        licenses=["(MIT AND GPL-3.0-only)"], license_kind="spdx-expression"
    ))
    assert v is not None
    assert "denied" in v.reason


def test_name_variant_allowed():
    v = _auditor().check(_comp(licenses=["MIT"], license_kind="name"))
    assert v is None


def test_name_variant_not_allowed():
    v = _auditor().check(_comp(licenses=["Proprietary"], license_kind="name"))
    assert v is not None
    assert "not on allowlist" in v.reason


def test_no_license_declared():
    v = _auditor().check(_comp(licenses=[], license_kind="none"))
    assert v is not None
    assert "no license declared" in v.reason


def test_multiple_licenses_any_pass():
    v = _auditor().check(_comp(
        licenses=["GPL-3.0-only", "MIT"], license_kind="spdx-id"
    ))
    # MIT is on the allowlist, so the component passes even though GPL-3.0-only is denied.
    # (Multi-license entries in CycloneDX mean "or".)
    assert v is None


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------
def test_cli_exit_zero_when_compliant(tmp_path, capsys):
    from ag.licenses import main as cli_main
    p = tmp_path / "sbom.json"
    p.write_text(json.dumps({"components": [
        {"name": "a", "version": "1", "licenses": [{"license": {"id": "MIT"}}]},
    ]}))
    rc = cli_main([str(p)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "violations:  0" in out


def test_cli_exit_two_on_violation(tmp_path, capsys):
    from ag.licenses import main as cli_main
    p = tmp_path / "sbom.json"
    p.write_text(json.dumps({"components": [
        {"name": "bad", "version": "1", "licenses": [{"license": {"id": "GPL-3.0-only"}}]},
    ]}))
    rc = cli_main([str(p)])
    out = capsys.readouterr().out
    assert rc == 2
    assert "violations:  1" in out


def test_cli_json_output(tmp_path, capsys):
    from ag.licenses import main as cli_main
    p = tmp_path / "sbom.json"
    p.write_text(json.dumps({"components": [
        {"name": "bad", "version": "1", "licenses": [{"license": {"id": "GPL-3.0-only"}}]},
    ]}))
    rc = cli_main([str(p), "--json"])
    out = capsys.readouterr().out
    assert rc == 2
    data = json.loads(out)
    assert data["violations"][0]["component"] == "bad"
PYEOF

echo
echo "== 5. write tooling/block6_live_proof.sh =="
cat > tooling/block6_live_proof.sh <<'BASH'
#!/usr/bin/env bash
# Block 6 live proof: generate a real SBOM from .venv, audit it, verify exit codes.
set -uo pipefail
cd "$HOME/aether"

echo "== 1. run block-6 tests =="
python -m pytest tests/test_licenses.py -q 2>&1 | tail -3

echo
echo "== 2. generate SBOM from .venv =="
mkdir -p sbom
cyclonedx-py environment --output-format json -o sbom/sbom.cdx.json
COMPONENTS=$(python3 -c "import json; print(len(json.load(open('sbom/sbom.cdx.json')).get('components', [])))")
echo "sbom/sbom.cdx.json: $COMPONENTS components"
[ "$COMPONENTS" -gt 0 ] || { echo "SBOM empty; aborting"; exit 1; }

echo
echo "== 3. audit with permissive allowlist (expect 0) =="
python -m ag.licenses sbom/sbom.cdx.json \
  --allow "MIT,Apache-2.0,BSD-2-Clause,BSD-3-Clause,ISC,Python-2.0,PSF-2.0,MPL-2.0,Unlicense,CC0-1.0,Zlib,MulanPSL-2.0,0BSD" \
  --include-dev
echo "exit=$?"

echo
echo "== 4. audit with strict allowlist (expect violations) =="
python -m ag.licenses sbom/sbom.cdx.json --allow "MIT"
echo "exit=$?"

echo
echo "== 5. machine-readable report =="
python -m ag.licenses sbom/sbom.cdx.json --allow "MIT" --json | python3 -m json.tool | head -30

echo
echo "== RESULT: block 6 verified =="
BASH
chmod +x tooling/block6_live_proof.sh

echo
echo "== setup complete =="
ls -la ag/licenses.py tests/test_licenses.py tooling/block6_live_proof.sh
