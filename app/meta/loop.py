"""Meta-loop — propose, review, apply, verify, rollback."""
from __future__ import annotations

import ast
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.meta import human as human_mod
from app.meta.observer import Observation, observe
from app.meta.proposer import propose
from app.meta.staging import Staging


@dataclass
class IterationResult:
    iteration: int
    accepted: bool
    reason: str
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    diff_len: int = 0
    elapsed_s: float = 0.0


def _parses(source: str) -> bool:
    try:
        ast.parse(source)
        return True
    except SyntaxError:
        return False


def _summarize(obs: Observation) -> dict[str, Any]:
    return {
        "mean": round(obs.mean, 4),
        "axis_pass": obs.axis_pass,
        "n": obs.n,
    }


def iterate(target: str,
            harness: str = "usefulness",
            max_iters: int = 5,
            auto: str | None = None,
            root: str = ".",
            swarm=None,
            log_path: str = ".meta_stage/loop.jsonl") -> list[IterationResult]:
    if swarm is None:
        from app.origami.swarm import Swarm
        swarm = Swarm(n_workers=1)

    stage = Staging(root)
    log_p = Path(root) / log_path
    log_p.parent.mkdir(parents=True, exist_ok=True)

    results: list[IterationResult] = []
    real = Path(root) / target

    for i in range(max_iters):
        t0 = time.time()
        before = observe(harness)
        if before.all_pass:
            results.append(IterationResult(
                iteration=i, accepted=False, reason="already_passing",
                before=_summarize(before),
            ))
            break

        source = real.read_text()
        try:
            patch = propose(target, source, before, swarm)
        except Exception as e:
            results.append(IterationResult(
                iteration=i, accepted=False,
                reason=f"propose_error: {type(e).__name__}",
                before=_summarize(before),
            ))
            continue

        if not patch or not _parses(patch):
            results.append(IterationResult(
                iteration=i, accepted=False, reason="patch_does_not_parse",
                before=_summarize(before), diff_len=len(patch or ""),
            ))
            continue

        staged = stage.propose(target, patch)
        diff = stage.diff(target)

        decision = human_mod.review(target, diff, before, staged, auto=auto)
        if decision == "edit":
            edited = human_mod.edit(staged)
            if not _parses(edited):
                stage.revert(target)
                results.append(IterationResult(
                    iteration=i, accepted=False, reason="edit_does_not_parse",
                    before=_summarize(before),
                ))
                continue
            stage.propose(target, edited)
        if decision == "reject":
            stage.revert(target)
            results.append(IterationResult(
                iteration=i, accepted=False, reason="human_rejected",
                before=_summarize(before), diff_len=len(diff),
            ))
            continue

        snap = stage.apply(target)
        if not _parses(real.read_text()):
            stage.rollback(target, snap)
            stage.revert(target)
            results.append(IterationResult(
                iteration=i, accepted=False, reason="applied_does_not_parse",
                before=_summarize(before), diff_len=len(diff),
            ))
            continue

        after = observe(harness)
        if after.mean > before.mean:
            stage.revert(target)  # clear proposal
            r = IterationResult(
                iteration=i, accepted=True, reason="improved",
                before=_summarize(before), after=_summarize(after),
                diff_len=len(diff), elapsed_s=time.time() - t0,
            )
        else:
            stage.rollback(target, snap)
            stage.revert(target)
            r = IterationResult(
                iteration=i, accepted=False, reason="no_improvement",
                before=_summarize(before), after=_summarize(after),
                diff_len=len(diff), elapsed_s=time.time() - t0,
            )
        results.append(r)
        with log_p.open("a") as f:
            f.write(json.dumps({
                "iteration": r.iteration,
                "accepted": r.accepted,
                "reason": r.reason,
                "before": r.before,
                "after": r.after,
                "target": target,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }) + "\n")

    return results
