#!/usr/bin/env python3
"""Bridge ASF grammar to actual tree symbols and references."""
from __future__ import annotations
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAMMAR = ROOT / "vatican" / "proof" / "asf_component_grammar.ebnf"
REPORT_JSON = ROOT / "bridge" / "asf_tree_report.json"
REPORT_MD = ROOT / "bridge" / "asf_tree_report.md"
INVENTORY = ROOT / "vatican" / "proof" / "asf_inventory.json"

SKIP_DIRS = {".git", ".venv", ".lanes", "node_modules", ".next", "__pycache__",
             ".mypy_cache", ".ruff_cache", ".hypothesis", ".pytest_cache",
             "site-packages", ".codeql-results", ".mesh-codeql-db",
             ".snapshots", ".delta", ".last-backups", ".complete-backups",
             "_grammar_spec"}

COMPONENT_RE = re.compile(r"\b(GOV|CMP|COG)-(KRN|IAM|POL|INF|CAP|EVD|ADM|FED|CTL|TRU|RES|EXE|DAT|ECO|INT|CORE|REA|CMP|ASSUR)-\d{3}\b")


def load_grammar_ids():
    text = GRAMMAR.read_text()
    stripped = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
    return sorted(set(m.group(0) for m in COMPONENT_RE.finditer(stripped)))


def load_indexes():
    out = []
    for idx in sorted(ROOT.rglob("_grammar_spec/index.json")):
        if any(part in SKIP_DIRS for part in idx.parts):
            continue
        try:
            out.append({"path": str(idx.relative_to(ROOT)),
                        "data": json.loads(idx.read_text())})
        except Exception as e:
            print(f"  cannot read {idx}: {e}", file=sys.stderr)
    return out


def scan_references():
    hits = {}
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix not in {".py",".md",".json",".yaml",".yml",".tla",".js",".ts",".tsx",".qmd",".ebnf"}:
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        for m in COMPONENT_RE.finditer(text):
            hits.setdefault(m.group(0), []).append(str(p.relative_to(ROOT)))
    return hits


@dataclass
class ComponentStatus:
    id: str
    referenced_by: list = field(default_factory=list)
    symbols_matched: list = field(default_factory=list)
    status: str = "missing"


def classify(asf_id, indexes, refs):
    st = ComponentStatus(id=asf_id)
    st.referenced_by = refs.get(asf_id, [])[:10]
    family = asf_id.split("-")[1].lower()
    for entry in indexes:
        for mod in entry["data"].get("modules", []):
            mod_name = (mod.get("name") or "").lower()
            if family in mod_name:
                for sym in mod.get("symbols", []):
                    st.symbols_matched.append(f"{mod['name']}.{sym.get('qualname', sym.get('name','?'))}")
    if st.symbols_matched and st.referenced_by:
        st.status = "implemented"
    elif st.symbols_matched:
        st.status = "partial"
    elif st.referenced_by:
        st.status = "referenced"
    else:
        st.status = "missing"
    return st


def main():
    if not GRAMMAR.exists():
        print(f"grammar not found: {GRAMMAR}")
        return 1
    asf_ids = load_grammar_ids()
    print(f"ASF components in grammar: {len(asf_ids)}")
    indexes = load_indexes()
    print(f"package indexes loaded: {len(indexes)}")
    refs = scan_references()
    print(f"ASF IDs referenced anywhere in tree: {len(refs)}")
    INVENTORY.write_text(json.dumps({
        "found_component_ids": sorted(refs.keys()),
        "counts": {"total": len(refs), "grammar_total": len(asf_ids)},
        "references": {k: v[:5] for k, v in sorted(refs.items())},
    }, indent=2))
    statuses = [classify(cid, indexes, refs) for cid in asf_ids]
    buckets = {"implemented":0,"partial":0,"referenced":0,"missing":0}
    for st in statuses:
        buckets[st.status] += 1
    REPORT_JSON.write_text(json.dumps({
        "grammar_total": len(asf_ids),
        "indexes_loaded": len(indexes),
        "tree_references": len(refs),
        "bucket_counts": buckets,
        "components": [asdict(st) for st in statuses],
    }, indent=2))
    md = ["# ASF <> Tree Bridge Report", "",
          f"- ASF components: **{len(asf_ids)}**",
          f"- Package indexes loaded: **{len(indexes)}**",
          f"- ASF IDs referenced in tree: **{len(refs)}**", "",
          "## Status buckets", "", "| Status | Count |", "|---|---:|"]
    for k in ("implemented","partial","referenced","missing"):
        md.append(f"| {k} | {buckets[k]} |")
    md += ["", "## Per component", "",
           "| Component | Status | Symbols | Referenced by |", "|---|---|---:|---|"]
    for st in statuses:
        r = ", ".join(st.referenced_by[:2]) if st.referenced_by else "—"
        md.append(f"| `{st.id}` | {st.status} | {len(st.symbols_matched)} | {r} |")
    REPORT_MD.write_text("\n".join(md))
    print()
    print("=== bridge summary ===")
    for k in ("implemented","partial","referenced","missing"):
        print(f"  {k:12s} {buckets[k]:3d}")
    print()
    print(f"wrote {REPORT_JSON.relative_to(ROOT)}")
    print(f"wrote {REPORT_MD.relative_to(ROOT)}")
    print(f"wrote {INVENTORY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
