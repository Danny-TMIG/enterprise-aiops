"""Healer — executes bounded, idempotent remedies."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Remedy:
    name: str
    fn: Callable[[dict[str, Any]], dict[str, Any]]
    max_calls_per_minute: int = 6

    def __hash__(self) -> int:
        return hash(self.name)


class Healer:
    def __init__(self) -> None:
        self._remedies: dict[str, Remedy] = {}
        self._calls: dict[str, list[float]] = {}
        self._history: list[dict[str, Any]] = []

    def register(self, remedy: Remedy) -> Healer:
        self._remedies[remedy.name] = remedy
        return self

    def available(self) -> list[str]:
        return list(self._remedies)

    def apply(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        import time
        r = self._remedies.get(name)
        if r is None:
            return {"ok": False, "error": "unknown remedy"}
        now = time.time()
        window = [t for t in self._calls.get(name, []) if now - t < 60]
        if len(window) >= r.max_calls_per_minute:
            return {"ok": False, "error": "rate limited"}
        window.append(now)
        self._calls[name] = window
        try:
            result = r.fn(params)
            record = {"remedy": name, "ok": True, "result": result, "ts": _now()}
        except Exception as exc:  # noqa: BLE001
            record = {"remedy": name, "ok": False, "error": type(exc).__name__, "ts": _now()}
        self._history.append(record)
        return record

    def history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]


class SystemHealer:

    """Runs health checks and applies registered fixes.

    A check is (name, check_fn, fix_fn). `check_and_heal()` runs every
    check, calls its fix when the check fails, and returns the list of
    actions taken. Keeps a history of every heal pass.
    """
    def __init__(self):
        self._checks: list = []
        self.history: list = []

    def add_check(self, name: str, check_fn, fix_fn=None) -> SystemHealer:
        self._checks.append((name, check_fn, fix_fn))
        return self

    def check_and_heal(self) -> list:
        actions: list = []
        for name, check_fn, fix_fn in self._checks:
            try:
                ok = bool(check_fn())
            except Exception as exc:
                ok = False
                err = f"{type(exc).__name__}: {exc}"
            else:
                err = None
            if ok:
                continue
            if fix_fn is None:
                actions.append({"check": name, "action": "no_fix",
                                "reason": err or "check failed"})
                continue
            try:
                fix_fn()
                actions.append({"check": name, "action": "healed"})
            except Exception as exc:
                actions.append({"check": name, "action": "heal_failed",
                                "reason": f"{type(exc).__name__}: {exc}"})
        self.history.append(actions)
        return actions

    @property
    def n_checks(self) -> int:
        return len(self._checks)

