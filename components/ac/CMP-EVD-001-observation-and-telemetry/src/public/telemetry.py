"""CMP-EVD-001 — Observation and Telemetry (full).

Captures runtime facts (hardware, load, memory) with source, time, and
integrity. Returns typed ObservationEvent records.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class ObservationEvent:
    event_id: str
    source: str
    metrics: dict[str, Any]
    created_at: float
    seal: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source": self.source,
            "metrics": self.metrics,
            "created_at": self.created_at,
            "seal": self.seal,
        }


def _seal(obj: dict[str, Any]) -> str:
    payload = {k: v for k, v in obj.items() if k != "seal"}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class TelemetryCollector:
    def __init__(self, source: str = "node.local"):
        self.source = source
        self._events: list[ObservationEvent] = []

    def capture(self) -> ObservationEvent:
        metrics: dict[str, Any] = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count() or 0,
        }
        try:
            import psutil

            metrics["cpu_load_percent"] = psutil.cpu_percent(interval=0.1)
            metrics["ram_usage_percent"] = psutil.virtual_memory().percent
            metrics["disk_usage_percent"] = psutil.disk_usage("/").percent
        except ImportError:
            metrics["cpu_load_percent"] = None
            metrics["ram_usage_percent"] = None
            metrics["disk_usage_percent"] = None
        e = ObservationEvent(f"obs-{uuid.uuid4().hex[:12]}", self.source, metrics, time.time())
        e.seal = _seal(
            {
                "event_id": e.event_id,
                "source": e.source,
                "metrics": e.metrics,
                "created_at": e.created_at,
            }
        )
        self._events.append(e)
        return e

    def events(self) -> list[ObservationEvent]:
        return list(self._events)

    def verify(self, event_id: str) -> bool:
        for e in self._events:
            if e.event_id == event_id:
                check = {
                    "event_id": e.event_id,
                    "source": e.source,
                    "metrics": e.metrics,
                    "created_at": e.created_at,
                }
                return _seal(check) == e.seal
        raise ValueError(f"unknown event {event_id}")
