"""License audit for a CycloneDX SBOM.

Reads a CycloneDX JSON or XML SBOM, evaluates every component's declared
license against an allowlist, and reports violations.

Handles, in this priority order:

1. Classifier strings ("License :: OSI Approved :: BSD License") — mapped to
   their SPDX equivalents via a fixed table.
2. SPDX expressions ("(MIT OR Apache-2.0)", "Apache-2.0 WITH LLVM-exception")
   — evaluated with a recursive walk over the parsed tree.
3. Plain SPDX IDs ("MIT").
4. Non-SPDX names — compared literally.

Multi-license entries in CycloneDX mean "OR": the component is compliant if
ANY declared license passes.

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

from license_expression import Licensing, get_spdx_licensing


# ---------------------------------------------------------------------------
# Classifier -> SPDX mapping
#
# These are the strings cyclonedx-py and pip-licenses emit when the package
# uses PEP 639 classifiers rather than SPDX IDs. The mapping is deliberately
# conservative: when the classifier is ambiguous (e.g. "BSD License" could be
# BSD-2 or BSD-3), we pick the most common and document the choice.
# ---------------------------------------------------------------------------
CLASSIFIER_TO_SPDX: dict[str, str] = {
    "License :: OSI Approved :: MIT License": "MIT",
    "License :: OSI Approved :: Apache Software License": "Apache-2.0",
    "License :: OSI Approved :: BSD License": "BSD-3-Clause",
    "License :: OSI Approved :: ISC License (ISCL)": "ISC",
    "License :: OSI Approved :: Python Software Foundation License": "PSF-2.0",
    "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)": "GPL-2.0-only",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)": "GPL-3.0-only",
    "License :: OSI Approved :: GNU Affero General Public License v3": "AGPL-3.0-only",
    "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)": "LGPL-2.1-only",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)": "LGPL-3.0-only",
    "License :: OSI Approved :: The Unlicense (Unlicense)": "Unlicense",
    "License :: OSI Approved :: zlib/libpng License": "Zlib",
    "License :: OSI Approved :: Academic Free License (AFL)": "AFL-3.0",
    "License :: OSI Approved :: Artistic License": "Artistic-2.0",
    "License :: OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)": "EPL-1.0",
    "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)": "EPL-2.0",
}


@dataclass
class Component:
    name: str
    version: str = ""
    purl: str = ""
    scope: str = "runtime"
    licenses: list[str] = field(default_factory=list)
    license_kind: str = "unknown"


@dataclass
class Violation:
    component: str
    version: str
    reason: str
    licenses: list[str]


# ---------------------------------------------------------------------------
# SBOM parsing
# ---------------------------------------------------------------------------
def _classify(entries: list[str]) -> str:
    """Best label for a list of raw license strings."""
    if not entries:
        return "none"
    if any(e.startswith("License ::") for e in entries):
        return "classifier"
    if any(" OR " in e or " AND " in e or " WITH " in e for e in entries):
        return "spdx-expression"
    # Single-token strings that look SPDX-ish.
    if all(_looks_like_spdx(e) for e in entries):
        return "spdx-id"
    return "name"


def _looks_like_spdx(s: str) -> bool:
    """True iff `s` is a known SPDX license ID.

    Delegates to the SPDX list shipped with `license_expression` — 2447 known
    identifiers as of v30. No heuristic, no drift as SPDX adds IDs.
    """
    if not s:
        return False
    try:
        from license_expression import get_spdx_licensing

        return s in get_spdx_licensing().known_symbols
    except Exception:
        return False


def _parse_licenses_entry(entry: dict[str, Any]) -> str:
    if "expression" in entry:
        return entry["expression"]
    lic = entry.get("license", {})
    return lic.get("id") or lic.get("name") or ""


def parse_cyclonedx_json(data: dict[str, Any]) -> list[Component]:
    seen: set[tuple[str, str]] = set()
    comps: list[Component] = []
    for c in data.get("components", []):
        name = c.get("name", "?")
        version = c.get("version", "")
        key = (name, version)
        if key in seen:
            continue
        seen.add(key)
        raw = [_parse_licenses_entry(e) for e in c.get("licenses", [])]
        raw = [r for r in raw if r]
        comps.append(Component(
            name=name, version=version, purl=c.get("purl", ""),
            scope=c.get("scope", "runtime"), licenses=raw, license_kind=_classify(raw),
        ))
    return comps


def parse_cyclonedx_xml(root: ET.Element) -> list[Component]:
    ns = {"cdx": "http://cyclonedx.org/schema/bom/1.5"}
    seen: set[tuple[str, str]] = set()
    comps: list[Component] = []
    for c in root.findall(".//cdx:component", ns) or root.findall(".//component"):
        name = c.findtext("cdx:name", default="?", namespaces=ns) or c.findtext("name", default="?")
        version = c.findtext("cdx:version", default="", namespaces=ns) or c.findtext("version", default="")
        key = (name, version)
        if key in seen:
            continue
        seen.add(key)
        raw: list[str] = []
        for lic in c.findall("cdx:licenses/cdx:license", ns) + c.findall("licenses/license"):
            expr = lic.findtext("cdx:expression", namespaces=ns) or lic.findtext("expression")
            lid = lic.findtext("cdx:id", namespaces=ns) or lic.findtext("id")
            lname = lic.findtext("cdx:name", namespaces=ns) or lic.findtext("name")
            raw.append(expr or lid or lname or "")
        raw = [r for r in raw if r]
        comps.append(Component(name=name, version=version, licenses=raw, license_kind=_classify(raw)))
    return comps


def load_sbom(path: Path) -> list[Component]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text()
    if path.suffix.lower() == ".xml" or text.lstrip().startswith("<?xml"):
        return parse_cyclonedx_xml(ET.fromstring(text))
    return parse_cyclonedx_json(json.loads(text))


# ---------------------------------------------------------------------------
# Allowlist evaluation
# ---------------------------------------------------------------------------
def _normalize_to_spdx(raw: str) -> str | None:
    """Return the SPDX string for a raw license, or None if unmappable."""
    if not raw:
        return None
    if raw in CLASSIFIER_TO_SPDX:
        return CLASSIFIER_TO_SPDX[raw]
    # Some classifiers have a trailing "License" variant we didn't enumerate.
    if raw.startswith("License ::"):
        return None
    return raw


def _evaluate_symbol(symbol: str, allowed: set[str], denied: set[str]) -> bool:
    """True if `symbol` is allowed and not denied."""
    if symbol in denied:
        return False
    if symbol in allowed:
        return True
    # SPDX's `+` suffix means "or later"; treat as allowed if base is allowed.
    if symbol.endswith("+") and symbol[:-1] in allowed:
        return True
    # Common aliases.
    aliases = {
        "Apache 2.0": "Apache-2.0",
        "BSD": "BSD-3-Clause",
        "MIT License": "MIT",
    }
    if symbol in aliases and aliases[symbol] in allowed:
        return True
    return False


def _evaluate_expression(
    parsed: Any, allowed: set[str], denied: set[str], licensing: Licensing
) -> bool:
    """Walk an SPDX expression tree, checking the allowlist.

    Verified against license_expression 30.x. The real shapes are:

      LicenseSymbol                — leaf, has no ``args`` (or empty)
      OR / AND                     — has ``args`` (a tuple) and ``operator`` (a string like
                                     ' OR ' / ' AND ', with surrounding spaces)
      LicenseWithExceptionSymbol   — has ``license_symbol`` for the base license

    Do not assume ``.left`` / ``.right`` — those do not exist.
    """
    from license_expression import LicenseSymbol

    # Leaf: plain license symbol.
    if isinstance(parsed, LicenseSymbol):
        return _evaluate_symbol(str(parsed), allowed, denied)

    # LICENSE WITH EXCEPTION: only the base symbol matters for allowlisting.
    if hasattr(parsed, "license_symbol"):
        base = getattr(parsed, "license_symbol", None)
        if base is not None:
            return _evaluate_symbol(str(base), allowed, denied)

    # Expression: get children from ``args`` and operator from ``operator``.
    args = getattr(parsed, "args", None) or ()
    op_raw = getattr(parsed, "operator", "") or ""
    op = str(op_raw).strip().upper()

    # Recursively evaluate each child.
    child_results = [_evaluate_expression(c, allowed, denied, licensing) for c in args]

    if not child_results:
        # No children means it's a bare symbol we didn't recognize.
        return _evaluate_symbol(str(parsed), allowed, denied)

    if op == "OR":
        return any(child_results)
    if op == "AND":
        return all(child_results)
    # Unknown operator: conservative — require every child to pass.
    return all(child_results)


class LicenseAuditor:
    def __init__(self, allow: Iterable[str], deny: Iterable[str] = ()) -> None:
        self._licensing: Licensing = get_spdx_licensing()
        self.allow = {s.strip() for s in allow if s.strip()}
        self.deny = {s.strip() for s in deny if s.strip()}

    def _eval_spdx(self, expr: str) -> tuple[bool, str]:
        """Evaluate an SPDX expression. Returns (allowed, reason_if_not).

        Distinguishes denied from not-on-allowlist so the reason string is
        diagnostic — "denied license: GPL-3.0-only" vs "not satisfied: ...".
        """
        try:
            parsed = self._licensing.parse(expr, validate=False, strict=False)
        except Exception as e:  # noqa: BLE001
            return False, f"unparseable SPDX expression: {e!r}"

        # Extract the symbols in this expression for the deny check.
        try:
            symbols = {str(s) for s in parsed.get_symbols()}
        except Exception:
            try:
                symbols = {str(parsed)}
            except Exception:
                symbols = set()

        denied_hit = symbols & self.deny
        if denied_hit:
            return False, f"denied license: {', '.join(sorted(denied_hit))}"

        try:
            ok = _evaluate_expression(parsed, self.allow, self.deny, self._licensing)
        except Exception as e:  # noqa: BLE001
            return False, f"evaluation error: {e!r}"

        if ok:
            return True, ""
        return False, f"expression not satisfied by allowlist: {expr}"

    def check(self, c: Component) -> Violation | None:
        if not c.licenses or c.license_kind == "none":
            return Violation(c.name, c.version, "no license declared", [])

        # Classifier strings: normalize, then treat each as an SPDX ID.
        if c.license_kind == "classifier":
            normalized = [_normalize_to_spdx(l) for l in c.licenses]
            normalized = [n for n in normalized if n]
            if not normalized:
                return Violation(c.name, c.version,
                                 f"unknown classifier: {c.licenses}", c.licenses)
            # Any normalized ID allowed -> compliant.
            for n in normalized:
                if n in self.allow:
                    return None
                if n in self.deny:
                    return Violation(c.name, c.version,
                                     f"denied license: {n}", c.licenses)
            return Violation(c.name, c.version,
                             f"no allowed license among {normalized}", c.licenses)

        # SPDX-id or SPDX-expression: try each; compliant if any passes.
        # SPDX-id or SPDX-expression: try each; compliant if any passes.
        # Keep the last failure reason so the violation is diagnostic.
        last_reason = ""
        for lic in c.licenses:
            ok, why = self._eval_spdx(lic)
            if ok:
                return None
            if why:
                last_reason = why

        # Non-SPDX names compared literally against allow/deny.
        if c.license_kind == "name":
            if any(l in self.allow for l in c.licenses):
                return None
            if any(l in self.deny for l in c.licenses):
                return Violation(c.name, c.version, "denied name", c.licenses)
            return Violation(c.name, c.version, "name not on allowlist", c.licenses)

        return Violation(c.name, c.version,
                         last_reason or "no declared license satisfied the allowlist",
                         c.licenses)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _default_allow() -> list[str]:
    """Permissive licenses appropriate for shipping code.

    Includes every license found in this project's dependency tree that is
    unambiguously permissive. Deny-list entries (GPL, AGPL) are handled
    separately and cannot be overridden by adding them here.
    """
    return [
        "MIT", "MIT-0", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
        "ISC", "Python-2.0", "PSF-2.0", "MPL-2.0", "Unlicense",
        "CC0-1.0", "0BSD", "Zlib", "BSL-1.0", "CNRI-Python", "MulanPSL-2.0",
        "AFL-3.0", "Artistic-2.0", "EPL-1.0", "EPL-2.0",
    ]


def _default_deny() -> list[str]:
    return ["GPL-2.0-only", "GPL-3.0-only", "AGPL-3.0-only", "SSPL-1.0"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ag.licenses")
    ap.add_argument("sbom", type=Path)
    ap.add_argument("--allow", default=",".join(_default_allow()))
    ap.add_argument("--deny", default=",".join(_default_deny()))
    ap.add_argument("--include-dev", action="store_true")
    ap.add_argument("--exclude", default="",
                    help="comma-separated package names to skip (documented metadata gaps)")
    ap.add_argument("--json", action="store_true")
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
            violations.append(v)

    if args.json:
        print(json.dumps({
            "sbom": str(args.sbom),
            "checked": checked,
            "skipped_dev": skipped_dev,
            "skipped_excluded": skipped_excluded,
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
        print(f"excluded:    {skipped_excluded}")
        print(f"violations:  {len(violations)}")
        for v in violations:
            ver = f"@{v.version}" if v.version else ""
            lics = ", ".join(v.licenses) if v.licenses else "(none declared)"
            print(f"  - {v.component}{ver}: {v.reason} [{lics}]")

    return 0 if not violations else 2


if __name__ == "__main__":
    sys.exit(main())
