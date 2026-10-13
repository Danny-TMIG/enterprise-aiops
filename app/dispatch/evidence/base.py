from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class EvidenceRecord:
    kind: str
    subject: str
    payload: dict[str, Any]
    id: str = ""
    ts: str = field(default_factory=_now)
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            blob = json.dumps(self.payload, sort_keys=True, default=str)
            self.hash = hashlib.sha256(
                (self.kind + self.subject + blob).encode()
            ).hexdigest()
        if not self.id:
            self.id = f"ev-{self.hash[:12]}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "kind": self.kind, "subject": self.subject,
            "payload": self.payload, "hash": self.hash, "ts": self.ts,
        }


class EvidenceStore:
    name = "evidence"
    def available(self) -> bool: return True
    def record(self, record: EvidenceRecord) -> dict[str, Any]:
        try:
            return self._record(record)
        except Exception as exc:  # noqa: BLE001
            return {"store": self.name, "status": "EXECUTION_FAILURE",
                    "error": type(exc).__name__}
    def _record(self, r: EvidenceRecord) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError
