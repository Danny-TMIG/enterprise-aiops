from __future__ import annotations
from typing import Any, Dict, List

from app.dispatch.scan.base import Scanner, ScanResult
from app.dispatch.scan.codeql import CodeQLScanner
from app.dispatch.scan.codacy import CodacyScanner


class ScanRegistry:
    def __init__(self) -> None:
        self.scanners: Dict[str, Scanner] = {
            "codeql": CodeQLScanner(),
            "codacy": CodacyScanner(),
        }

    def list(self) -> Dict[str, Any]:
        return {n: {"available": s.available()}
                for n, s in self.scanners.items()}

    def scan(self, name: str, root: str) -> ScanResult:
        s = self.scanners.get(name)
        if not s:
            return ScanResult(scanner=name, status="UNSUPPORTED")
        return s.scan(root)

    def scan_all(self, root: str) -> List[ScanResult]:
        return [s.scan(root) for s in self.scanners.values()]
