"""SARIF parser + markdown renderer."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Finding:
    rule_id: str
    rule_name: str
    severity: str
    message: str
    file: str
    line: int
    column: int
    help_uri: str = ""
    tags: tuple = ()

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "help_uri": self.help_uri,
            "tags": list(self.tags),
        }


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    tool: str = "CodeQL"
    version: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.findings)

    def by_severity(self) -> dict[str, int]:
        c = Counter(f.severity for f in self.findings)
        return dict(c)

    def by_rule(self) -> dict[str, int]:
        c = Counter(f.rule_id for f in self.findings)
        return dict(c)

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "version": self.version,
            "total": self.total,
            "by_severity": self.by_severity(),
            "by_rule": self.by_rule(),
            "findings": [f.to_dict() for f in self.findings],
        }


def parse_sarif(path: Path) -> Report:
    if not path.exists():
        return Report()
    doc = json.loads(path.read_text())
    report = Report(raw=doc)
    for run in doc.get("runs", []):
        tool = run.get("tool", {}).get("driver", {})
        report.tool = tool.get("name", report.tool)
        report.version = tool.get("semanticVersion", report.version)
        rules = {r.get("id"): r for r in tool.get("rules", [])}
        for res in run.get("results", []):
            rid = res.get("ruleId", "")
            rule = rules.get(rid, {})
            msg = (res.get("message", {}) or {}).get("text", "")
            level = (res.get("level")
                     or rule.get("defaultConfiguration", {}).get("level")
                     or "warning")
            locations = res.get("locations", [])
            file = ""
            line = 0
            col = 0
            if locations:
                pl = locations[0].get("physicalLocation", {})
                file = (pl.get("artifactLocation", {}) or {}).get("uri", "")
                region = pl.get("region", {}) or {}
                line = int(region.get("startLine", 0) or 0)
                col = int(region.get("startColumn", 0) or 0)
            tags = tuple(rule.get("properties", {}).get("tags", []))
            report.findings.append(Finding(
                rule_id=rid,
                rule_name=rule.get("name", rid),
                severity=level,
                message=msg,
                file=file,
                line=line,
                column=col,
                help_uri=rule.get("helpUri", ""),
                tags=tags,
            ))
    return report


def summarize(report: Report) -> dict[str, Any]:
    return {
        "tool": report.tool,
        "version": report.version,
        "total": report.total,
        "by_severity": report.by_severity(),
        "top_rules": sorted(report.by_rule().items(),
                            key=lambda kv: -kv[1])[:10],
    }


def render_markdown(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"# CodeQL report — {report.tool} {report.version}")
    lines.append("")
    lines.append(f"Total findings: **{report.total}**")
    lines.append("")
    sev = report.by_severity()
    if sev:
        lines.append("## By severity")
        lines.append("")
        lines.append("| severity | count |")
        lines.append("|----------|-------|")
        for k in sorted(sev, key=lambda x: -sev[x]):
            lines.append(f"| {k} | {sev[k]} |")
        lines.append("")
    top = sorted(report.by_rule().items(), key=lambda kv: -kv[1])[:15]
    if top:
        lines.append("## Top rules")
        lines.append("")
        lines.append("| rule | count |")
        lines.append("|------|-------|")
        for k, n in top:
            lines.append(f"| `{k}` | {n} |")
        lines.append("")
    if report.findings:
        lines.append("## Findings")
        lines.append("")
        lines.append("| # | severity | rule | file:line | message |")
        lines.append("|---|----------|------|-----------|---------|")
        for i, f in enumerate(report.findings, 1):
            loc = f"{f.file}:{f.line}" if f.file else "-"
            msg = (f.message or "").replace("|", "\\|")[:160]
            lines.append(f"| {i} | {f.severity} | `{f.rule_id}` | "
                         f"{loc} | {msg} |")
        lines.append("")
    return "\n".join(lines)
