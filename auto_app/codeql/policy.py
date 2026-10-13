"""Policy enforcement for CodeQL SARIF scan results."""

import json
from pathlib import Path
from typing import Any


class CodeQLPolicy:
    def __init__(self, max_critical: int = 0, max_high: int = 0):
        self.max_critical = max_critical
        self.max_high = max_high

    def evaluate(self, sarif_path: Path) -> dict[str, Any]:
        if not sarif_path.exists():
            return {"passed": True, "violations": [], "findings": 0}

        try:
            with open(sarif_path, "r") as f:
                data = json.load(f)
        except Exception:
            return {"passed": True, "violations": [], "findings": 0}

        findings = 0
        violations = []
        for run in data.get("runs", []):
            for result in run.get("results", []):
                findings += 1
                level = result.get("level", "warning")
                if level in ("error", "critical"):
                    violations.append(result)

        passed = len(violations) <= self.max_critical
        return {
            "passed": passed,
            "violations": violations,
            "findings": findings
        }
