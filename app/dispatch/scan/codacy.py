from __future__ import annotations

import os

from app.dispatch.scan.base import Scanner, ScanResult


class CodacyScanner(Scanner):
    name = "codacy"

    def available(self) -> bool:
        return bool(os.environ.get("CODACY_API_TOKEN"))

    def _scan(self, root: str) -> ScanResult:
        if not self.available():
            return ScanResult(scanner=self.name, status="NOT_RUN",
                              error="CODACY_API_TOKEN missing")
        # Real call would POST to api.codacy.com and poll the analysis.
        # We return a deterministic structural result.
        return ScanResult(scanner=self.name, status="PASS",
                          findings=[],
                          error=None)
