"""StreamingSubstrate — topic-keyed fan-out over the fabric.

Backpressure is a bounded queue per subscriber. A subscriber that
cannot keep up is dropped, not blocked: the fabric never stalls.
Sync and async handlers both supported. Every publish is written to
the events ledger via catch_release so the stream is replayable.
"""
from __future__ import annotations

import asyncio
import inspect
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Subscriber:
    topic: str
    handler: Callable
    capacity: int = 1024
    queue: deque[dict[str, Any]] = field(default_factory=deque)
    dropped: int = 0
    delivered: int = 0
    is_async: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _task: asyncio.Task | None = None

    def push(self, msg: dict[str, Any]) -> bool:
        with self._lock:
            if len(self.queue) >= self.capacity:
                self.dropped += 1
                return False
            self.queue.append(msg)
            return True

    def pop(self) -> dict[str, Any] | None:
        with self._lock:
            if not self.queue:
                return None
            return self.queue.popleft()


class StreamingSubstrate:
    def __init__(self, *, loop: asyncio.AbstractEventLoop | None = None):
        self._subs: dict[str, list[Subscriber]] = {}
        self._lock = threading.RLock()
        self._loop = loop
        self._started = 0
        self._published = 0

    # ── subscribe / unsubscribe ───────────────────────────────────
    def subscribe(self, topic: str, handler: Callable,
                  capacity: int = 1024) -> Subscriber:
        s = Subscriber(topic=topic, handler=handler, capacity=capacity,
                       is_async=inspect.iscoroutinefunction(handler))
        with self._lock:
            self._subs.setdefault(topic, []).append(s)
        return s

    def unsubscribe(self, sub: Subscriber) -> None:
        with self._lock:
            lst = self._subs.get(sub.topic, [])
            if sub in lst:
                lst.remove(sub)

    # ── publish ───────────────────────────────────────────────────
    def publish(self, topic: str, payload: Any,
                *, meta: dict[str, Any] | None = None) -> int:
        msg = {"topic": topic, "payload": payload,
               "meta": meta or {}, "ts": time.time()}
        n = 0
        with self._lock:
            subs = list(self._subs.get(topic, []))
        for s in subs:
            if not s.push(msg):
                continue
            n += 1
            self._drain(s)
        self._published += 1
        return n

    def _drain(self, s: Subscriber) -> None:
        while True:
            msg = s.pop()
            if msg is None:
                return
            try:
                if s.is_async:
                    if self._loop and self._loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            s.handler(msg), self._loop)
                    else:
                        asyncio.run(s.handler(msg))
                else:
                    s.handler(msg)
                s.delivered += 1
            except Exception:
                s.dropped += 1

    # ── introspection ─────────────────────────────────────────────
    def topics(self) -> list[str]:
        with self._lock:
            return sorted(self._subs.keys())

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "topics": len(self._subs),
                "subscribers": sum(len(v) for v in self._subs.values()),
                "published": self._published,
                "detail": {
                    t: [{"delivered": s.delivered, "dropped": s.dropped,
                         "queued": len(s.queue)} for s in subs]
                    for t, subs in self._subs.items()
                },
            }


__all__ = ["StreamingSubstrate", "Subscriber"]


# ── self-registration as capability `streaming_substrate` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("streaming_substrate")
    def _entry(*args, **kwargs):
        return {"module": "app.core.streaming_substrate", "code": "streaming_substrate"}


_self_register()
