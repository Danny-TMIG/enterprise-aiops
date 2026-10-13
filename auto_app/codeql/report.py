"""Reporting utilities for CodeQL results."""

import json
from pathlib import Path
from typing import Any


class CodeQLReporter:
    def __init__(self, results_path: Path):
        self.results_path = results_path

    def generate_summary(self) -> dict[str, Any]:
        if not self.results_path.exists():
            return {"status": "no_results", "total_issues": 0}

        try:
            with open(self.results_path, "r") as f:
                data = json.load(f)
        except Exception:
            return {"status": "error_reading_results", "total_issues": 0}

        total_issues = sum(len(run.get("results", [])) for run in data.get("runs", []))
        return {
            "status": "success",
            "total_issues": total_issues,
            "path": str(self.results_path)
        }
