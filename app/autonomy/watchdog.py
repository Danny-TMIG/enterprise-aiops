"""Watchdog — periodically samples probes and feeds the decision engine."""
from __future__ import annotations
import threading, time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from app.autonomy.decisions import Decision, DecisionEngine


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Probe:
    name: str
    fn: Callable[[], Dict[str, Any]]
    interval_s: float = 5.0


class Watchdog:
    def __init__(self, engine: Optional[DecisionEngine] = None, probes: Optional[List[Probe]] = None):
        if engine is None:
            from app.autonomy.decisions import DecisionEngine
            engine = DecisionEngine()
        self.engine = engine
        self.probes: List[Probe] = probes or []
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._last: Dict[str, Dict[str, Any]] = {}
        self._decisions: List[Decision] = []

    def add(self, probe: Probe) -> "Watchdog":
        self.probes.append(probe)
        return self

    def snapshot(self) -> Dict[str, Any]:
        obs: Dict[str, Any] = {"ts": _now()}
        for p in self.probes:
            try:
                obs[p.name] = p.fn()
            except Exception as exc:  # noqa: BLE001
                obs[p.name] = {"ok": False, "error": type(exc).__name__}
        return obs

    def step(self) -> List[Decision]:
        obs = self.snapshot()
        self._last = obs
        ds = self.engine.evaluate_all(obs) if self.engine is not None else []
        self._decisions.extend(ds)
        return ds

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _loop(self) -> None:
        # Simple loop: one step per second; probes carry their own interval
        while not self._stop.is_set():
            try:
                self.step()
            except Exception:
                pass
            time.sleep(1.0)

    def last_observation(self) -> Dict[str, Any]:
        return self._last

    def recent_decisions(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [d.to_dict() for d in self._decisions[-limit:]]


    def pulse(self) -> Dict[str, Any]:
        """Synchronous sample: run probes, evaluate, return the observation.

        Unlike `step()`, which returns the list of Decisions, `pulse`
        returns the full observation bundle so callers can log it.
        """
        obs = self.snapshot()
        self._last = obs
        decisions = (self.engine.evaluate(obs) or []
                     if self.engine is not None else [])
        self._decisions.extend(decisions)
        return {
            "ts": obs["ts"],
            "observations": {k: v for k, v in obs.items() if k != "ts"},
            "decisions": [
                d.to_dict() if hasattr(d, "to_dict") else dict(d)
                if isinstance(d, dict) else d
                for d in decisions
            ],
        }
