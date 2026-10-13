from __future__ import annotations

from app.dispatch.scan.base import Scanner, ScanResult


class CodeQLScanner(Scanner):
    name = "codeql"

    def available(self) -> bool:
        from app.mesh.codeql_runner import _codeql_bin
        return _codeql_bin() is not None

    def _scan(self, root: str) -> ScanResult:
        from app.mesh.codeql_runner import run_codeql
        sarif = run_codeql(root)
        if not sarif:
            return ScanResult(scanner=self.name, status="NOT_RUN",
                              error="codeql unavailable")
        import json
        from pathlib import Path
        try:
            data = json.loads(Path(sarif).read_text())
        except Exception:
            return ScanResult(scanner=self.name, status="UNKNOWN",
                              error="sarif unreadable")
        findings = []
        for run in data.get("runs", []):
            for r in run.get("results", []):
                findings.append({
                    "rule": r.get("ruleId"),
                    "message": r.get("message", {}).get("text", ""),
                })
        return ScanResult(scanner=self.name,
                          status="PASS" if not findings else "FAIL",
                          findings=findings)
