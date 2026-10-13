"""Swarm of local 7B workers.

Each worker is a LocalMLXProvider with its own prompt.  The swarm
shards long prompts via context.py and dispatches the shards in
parallel threads.  Model weights are shared — only the KV cache
and prompt differ per worker.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from app.dispatch.models.base import ModelRequest
from app.dispatch.models.local_mlx import LocalMLXProvider, _mlx_available


@dataclass
class WorkerResult:
    index: int
    text: str
    dry_run: bool
    provider: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "text": self.text,
                "dry_run": self.dry_run, "provider": self.provider,
                "model": self.model, "usage": self.usage}


@dataclass
class SwarmResult:
    workers: list[WorkerResult]
    stitched: str
    n_workers: int
    dry_run_all: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"n_workers": self.n_workers,
                "dry_run_all": self.dry_run_all,
                "workers": [w.to_dict() for w in self.workers],
                "stitched_chars": len(self.stitched)}


class Swarm:
    """N local workers.  Shared weights, per-worker prompts."""

    def __init__(self, n_workers: int = 4, model_id: str | None = None):
        self.n = n_workers
        self.model_id = model_id
        self._workers: list[LocalMLXProvider] = []
        for i in range(n_workers):
            p = LocalMLXProvider(f"swarm-{i}", model_id=model_id)
            self._workers.append(p)

    # ── single-shot ────────────────────────────────────────────
    def run_one(self, index: int, prompt: str,
                system: str | None = None,
                max_tokens: int = 256,
                temperature: float = 0.0) -> WorkerResult:
        if not self.available():
            head = prompt.strip().splitlines()[0][:120] if prompt.strip() else ""
            return WorkerResult(
                index=index,
                text=f"<unfilled:{head}>",
                dry_run=True,
                provider=f"swarm-{index % self.n}",
                model="",
                usage={},
            )
        w = self._workers[index % self.n]
        resp = w.complete(ModelRequest(
            task="coding", prompt=prompt, system=system,
            max_tokens=max_tokens, temperature=temperature,
        ))
        return WorkerResult(
            index=index, text=resp.text, dry_run=resp.dry_run,
            provider=resp.provider, model=resp.model,
            usage=resp.usage,
        )

    # ── parallel fan-out ──────────────────────────────────────
    def fan(self, prompts: list[str],
            system: str | None = None,
            max_tokens: int = 256,
            temperature: float = 0.0,
            workers: int | None = None) -> SwarmResult:
        workers = workers or self.n
        results: list[WorkerResult] = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(self.run_one, i, p, system,
                            max_tokens, temperature): i
                for i, p in enumerate(prompts)
            }
            for f in as_completed(futures):
                results.append(f.result())
        results.sort(key=lambda r: r.index)
        stitched = "\n---\n".join(r.text for r in results)
        return SwarmResult(
            workers=results, stitched=stitched, n_workers=self.n,
            dry_run_all=all(r.dry_run for r in results),
        )

    # ── double-double long context ────────────────────────────
    def run_double_double(self, text: str, instruction: str,
                          max_tokens: int = 256) -> SwarmResult:
        from app.origami.context import DoubleDouble, shard
        parts = [s.text for s in shard(text, n=4)]
        dd = DoubleDouble(parts=parts)

        # level 1: two workers each summarize half
        lvl1_prompts = [
            f"{instruction}\n\nPART 1:\n{dd.level1()[0]}",
            f"{instruction}\n\nPART 2:\n{dd.level1()[1]}",
        ]
        l1 = self.fan(lvl1_prompts, max_tokens=max_tokens, workers=2)

        # level 2: one worker merges the two summaries
        merged = "\n---\n".join(w.text for w in l1.workers)
        l2 = self.fan(
            [f"{instruction}\n\nMERGED HALVES:\n{merged}"],
            max_tokens=max_tokens, workers=1,
        )
        return SwarmResult(
            workers=l2.workers, stitched=l2.stitched,
            n_workers=self.n,
            dry_run_all=all(r.dry_run for r in l2.workers),
        )

    def available(self) -> bool:
        return _mlx_available()
