from __future__ import annotations

from typing import Any

from app.dispatch.evidence.aar import AARStore
from app.dispatch.evidence.base import EvidenceRecord, EvidenceStore
from app.dispatch.evidence.novafabric import NovaFabricStore


class EvidenceRegistry:
    def __init__(self) -> None:
        self.stores: dict[str, EvidenceStore] = {
            "novafabric": NovaFabricStore(),
            "aar-alc":    AARStore(),
        }

    def list(self) -> dict[str, Any]:
        return {n: {"available": s.available()}
                for n, s in self.stores.items()}

    def record(self, kind: str, subject: str,
               payload: dict[str, Any]) -> dict[str, Any]:
        r = EvidenceRecord(kind=kind, subject=subject, payload=payload)
        return {
            "record": r.to_dict(),
            "stores": [s.record(r) for s in self.stores.values()],
        }

    def record_to(self, store: str, kind: str, subject: str,
                  payload: dict[str, Any]) -> dict[str, Any]:
        s = self.stores.get(store)
        if not s:
            return {"status": "UNSUPPORTED", "store": store}
        r = EvidenceRecord(kind=kind, subject=subject, payload=payload)
        return s.record(r)
