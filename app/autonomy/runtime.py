"""Autonomous runtime — one process-wide instance."""
from __future__ import annotations

import os
from typing import Any

from app.autonomy.decisions import DecisionEngine
from app.autonomy.healer import Healer
from app.autonomy.policies import POLICIES
from app.autonomy.watchdog import Probe, Watchdog

_RUNTIME: Runtime | None = None


def _probe_db() -> dict[str, Any]:
    from app.db.health import db_health
    return db_health()


def _probe_metrics() -> dict[str, Any]:
    # Lightweight self-observed metrics. No external I/O.
    import os
    import resource
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes, Linux reports KB
    rss_mb = rss / (1024 * 1024) if rss > 1024 * 1024 else rss / 1024
    return {
        "error_rate": float(os.environ.get("TMIG_ERROR_RATE", "0.0")),
        "mem_pct": float(os.environ.get("TMIG_MEM_PCT", "0.0")),
        "rss_mb": round(rss_mb, 2),
    }


def _probe_kill_switch() -> dict[str, Any]:
    # Simulated; the C2 kill switch is per-instance, so we expose
    # a process-wide env-controlled view.
    engaged = os.environ.get("TMIG_KILL_SWITCH", "0") == "1"
    return {"engaged": engaged}


class Runtime:
    def __init__(self) -> None:
        self.engine = DecisionEngine()
        self.healer = Healer()
        for rule, remedy in POLICIES:
            self.engine.add(rule)
            self.healer.register(remedy)
        self.watchdog = Watchdog(self.engine, probes=[
            Probe(name="db",         fn=_probe_db,         interval_s=5.0),
            Probe(name="metrics",    fn=_probe_metrics,    interval_s=1.0),
            Probe(name="kill_switch", fn=_probe_kill_switch, interval_s=2.0),
        ])
        self._autostart = os.environ.get("TMIG_AUTONOMY", "1") == "1"

    def start(self) -> None:
        if self._autostart:
            self.watchdog.start()

    def stop(self) -> None:
        self.watchdog.stop()

    def step(self) -> dict[str, Any]:
        decisions = self.watchdog.step()
        applied = []
        for d in decisions:
            res = self.healer.apply(d.action, d.params)
            applied.append({"decision": d.to_dict(), "result": res})
        return {
            "observation": self.watchdog.last_observation(),
            "decisions": [d.to_dict() for d in decisions],
            "applied": applied,
        }


def get_runtime() -> Runtime:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = Runtime()
    return _RUNTIME


class AutonomyRuntime:

    """One process-wide tick: sample probes, evaluate, heal.

    Composes a Watchdog (samples probes, runs the DecisionEngine) and a
    SystemHealer (runs registered health checks and applies fixes).
    """
    def __init__(self, watchdog=None, healer=None):
        from app.autonomy.healer import SystemHealer
        from app.autonomy.watchdog import Watchdog
        self.watchdog = watchdog or Watchdog()
        self.healer = healer or SystemHealer()
        self.steps: int = 0
        self.history: list = []

    def step(self) -> dict:
        pulse = self.watchdog.pulse()
        heals = self.healer.check_and_heal()
        self.steps += 1
        record = {
            "step": self.steps,
            "ts": pulse.get("ts"),
            "decisions": pulse.get("decisions", []),
            "heal_actions": heals,
        }
        self.history.append(record)
        return record

    def run(self, n: int = 1) -> list:
        return [self.step() for _ in range(n)]

