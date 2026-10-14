"""CMP-EXE-004 — Scheduler.

Non-preemptive default per CMP-DEC-012. Preemption only when the request
carries `emergency_reserve=True` and the running job was placed with
`protect_from_preemption=False`.
"""
from __future__ import annotations
import heapq, time
from dataclasses import dataclass, field
from typing import Optional


class SchedulerError(RuntimeError):
    pass


@dataclass(order=True)
class _Job:
    priority: int
    submitted_at: float
    job_id: str = field(compare=False)
    cpu_cores: int = field(compare=False, default=1)
    memory_gb: int = field(compare=False, default=1)
    emergency_reserve: bool = field(compare=False, default=False)
    protect_from_preemption: bool = field(compare=False, default=True)


class Scheduler:
    def __init__(self, cpu_cores: int = 4, memory_gb: int = 16) -> None:
        if cpu_cores <= 0 or memory_gb <= 0:
            raise SchedulerError("capacity must be positive")
        self._cpu_cap = cpu_cores
        self._mem_cap = memory_gb
        self._cpu_used = 0
        self._mem_used = 0
        self._queue: list[_Job] = []
        self._running: dict[str, _Job] = {}
        self._seq = 0

    def submit(
        self,
        job_id: str,
        *,
        priority: int = 100,
        cpu_cores: int = 1,
        memory_gb: int = 1,
        emergency_reserve: bool = False,
        protect_from_preemption: bool = True,
    ) -> None:
        if job_id in self._running:
            raise SchedulerError(f"job {job_id} already running")
        if cpu_cores > self._cpu_cap or memory_gb > self._mem_cap:
            raise SchedulerError(f"job {job_id} exceeds capacity")
        self._seq += 1
        j = _Job(
            priority=priority,
            submitted_at=time.time(),
            job_id=job_id,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            emergency_reserve=emergency_reserve,
            protect_from_preemption=protect_from_preemption,
        )
        heapq.heappush(self._queue, (j, self._seq))

    def _fits(self, j: _Job) -> bool:
        return (self._cpu_used + j.cpu_cores <= self._cpu_cap
                and self._mem_used + j.memory_gb <= self._mem_cap)

    def _evict_for(self, j: _Job) -> Optional[str]:
        """Preemption allowed only for emergency_reserve jobs."""
        if not j.emergency_reserve:
            return None
        for rid, r in sorted(self._running.items(),
                             key=lambda kv: kv[1].priority, reverse=True):
            if r.protect_from_preemption:
                continue
            self._cpu_used -= r.cpu_cores
            self._mem_used -= r.memory_gb
            del self._running[rid]
            return rid
        return None

    def schedule(self) -> list[str]:
        placed: list[str] = []
        while self._queue:
            j, _ = heapq.heappop(self._queue)
            if self._fits(j):
                self._cpu_used += j.cpu_cores
                self._mem_used += j.memory_gb
                self._running[j.job_id] = j
                placed.append(j.job_id)
                continue
            evicted = self._evict_for(j)
            if evicted is None:
                # No preemption possible — put it back and stop.
                heapq.heappush(self._queue, (j, self._seq))
                break
            if self._fits(j):
                self._cpu_used += j.cpu_cores
                self._mem_used += j.memory_gb
                self._running[j.job_id] = j
                placed.append(j.job_id)
        return placed

    def finish(self, job_id: str) -> None:
        j = self._running.pop(job_id, None)
        if j is None:
            raise SchedulerError(f"job {job_id} not running")
        self._cpu_used -= j.cpu_cores
        self._mem_used -= j.memory_gb

    def stats(self) -> dict:
        return {
            "queued": len(self._queue),
            "running": list(self._running.keys()),
            "cpu_used": self._cpu_used,
            "cpu_cap": self._cpu_cap,
            "mem_used": self._mem_used,
            "mem_cap": self._mem_cap,
        }
