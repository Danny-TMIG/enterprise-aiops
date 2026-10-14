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
