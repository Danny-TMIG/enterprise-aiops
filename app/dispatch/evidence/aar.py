from __future__ import annotations
from typing import Any, Dict
from app.dispatch.evidence.base import EvidenceStore, EvidenceRecord


class AARStore(EvidenceStore):
    """After-Action Review / After-Action Learning Cycle.

    Records outcomes and distills them into a 'lesson' payload — the
    raw material the mesh uses to update routing and skill selection.
    """
    name = "aar-alc"
    def __init__(self) -> None:
        self._log: Dict[str, Dict[str, Any]] = {}

    def _record(self, r: EvidenceRecord) -> Dict[str, Any]:
        lesson = self._distill(r)
        self._log[r.id] = {**r.to_dict(), "lesson": lesson}
        return {"store": self.name, "status": "PASS",
                "id": r.id, "lesson": lesson}

    def _distill(self, r: EvidenceRecord) -> Dict[str, Any]:
        p = r.payload or {}
        outcome = p.get("status") or p.get("outcome") or "UNKNOWN"
        return {
            "outcome": outcome,
            "is_success": outcome == "PASS",
            "kind": r.kind,
        }
