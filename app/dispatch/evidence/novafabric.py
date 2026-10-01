from __future__ import annotations
from typing import Any, Dict
from app.dispatch.evidence.base import EvidenceStore, EvidenceRecord


class NovaFabricStore(EvidenceStore):
    """NovaFabric — content-addressed, signed evidence fabric.
    Locally we persist to memory + compute a stable content hash."""
    name = "novafabric"
    def __init__(self) -> None:
        self._log: Dict[str, Dict[str, Any]] = {}

    def _record(self, r: EvidenceRecord) -> Dict[str, Any]:
        self._log[r.id] = r.to_dict()
        return {"store": self.name, "status": "PASS",
                "id": r.id, "hash": r.hash}

    def get(self, id_: str) -> Dict[str, Any]:
        return self._log.get(id_) or {}
