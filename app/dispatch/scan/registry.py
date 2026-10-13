from __future__ import annotations

import builtins
from typing import Any

from app.dispatch.scan.base import Scanner, ScanResult
from app.dispatch.scan.codacy import CodacyScanner
from app.dispatch.scan.codeql import CodeQLScanner


class ScanRegistry:
    def __init__(self) -> None:
        self.scanners: dict[str, Scanner] = {
            "codeql": CodeQLScanner(),
            "codacy": CodacyScanner(),
        }

    def list(self) -> dict[str, Any]:
        return {n: {"available": s.available()}
                for n, s in self.scanners.items()}

    def scan(self, name: str, root: str) -> ScanResult:
        s = self.scanners.get(name)
        if not s:
            return ScanResult(scanner=name, status="UNSUPPORTED")
        return s.scan(root)

    def scan_all(self, root: str) -> builtins.list[ScanResult]:
        return [s.scan(root) for s in self.scanners.values()]
