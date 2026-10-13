"""Deterministic C2 simulation driver."""
from __future__ import annotations

from typing import Any

from app.botnetmastery.c2 import C2Server
from app.botnetmastery.models import Bot, Task


class Simulation:
    def __init__(self, server: C2Server,
                 seed: int | None = None,
                 *args, **kwargs):
        self.server = server
        self.seed = seed
        self._state = (seed or 0) & 0x7FFFFFFF
        self.broadcast_queue: list[dict[str, Any]] = []

    def _next(self) -> int:
        self._state = (1103515245 * self._state + 12345) & 0x7FFFFFFF
        return self._state

    def spawn(self, count: int = 1) -> list[str]:
        ids: list[str] = []
        for _ in range(count):
            tag = self._next() % 100000
            b = Bot.new(f"host-{tag}", "linux", "x86_64")
            self.server.register_bot(b)
            ids.append(b.id)
        return ids

    def queue_broadcast(self, action: str, payload: dict) -> None:
        self.broadcast_queue.append(
            {"action": action, "payload": dict(payload or {})})

    def tick(self) -> dict[str, int]:
        stats = {"heartbeats": 0, "dispatched": 0,
                 "completed": 0, "skipped": 0}
        if self.server.kill_switch_engaged():
            stats["skipped"] = len(self.server.list_bots())
            return stats

        active = self.server.list_bots(status="active")
        for b in active:
            try:
                self.server.heartbeat(b["id"])
                stats["heartbeats"] += 1
            except KeyError:
                stats["skipped"] += 1

        actions = list(self.broadcast_queue)
        self.broadcast_queue.clear()
        for act in actions:
            for b in active:
                self.server.queue_task(Task.new(
                    b["id"], act["action"], act["payload"]))

        for b in active:
            row = self.server.dispatch(b["id"])
            if row is None:
                stats["skipped"] += 1
                continue
            stats["dispatched"] += 1
            self.server.complete(row["id"], b["id"],
                                 '{"ok": true}', success=True)
            stats["completed"] += 1
        return stats


def run_simulation(
steps: int = 1,
    controller=None,
    bots=None,
    seed: int = 0):
    """Advance a C2 simulation by `steps` ticks. Returns the full timeline."""
    from app.botnetmastery.c2 import C2Controller
    from app.botnetmastery.models import BotModel
    if controller is None:
        controller = C2Controller(bots=bots, seed=seed)
        if bots is None:
            controller.add_bot(BotModel(id="bot-0", status="active"))
    timeline = []
    for _ in range(steps):
        timeline.append(controller.tick())
    return {
        "steps": steps,
        "events": timeline,
        "final": controller.poll(),
    }

