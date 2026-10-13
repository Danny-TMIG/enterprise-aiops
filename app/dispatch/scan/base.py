from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ScanResult:
    scanner: str
    status: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    ts: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scanner": self.scanner, "status": self.status,
            "findings": self.findings, "error": self.error, "ts": self.ts,
        }


class Scanner:
    name = "scanner"
    def available(self) -> bool: return True
    def scan(self, root: str) -> ScanResult:
        try:
            return self._scan(root)
        except Exception as exc:  # noqa: BLE001
            return ScanResult(scanner=self.name, status="EXECUTION_FAILURE",
                              error=type(exc).__name__)
    def _scan(self, root: str) -> ScanResult:  # pragma: no cover
        raise NotImplementedError
