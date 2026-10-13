"""Proposer — ask the local model for a patch."""
from __future__ import annotations

import json

from app.meta.observer import Observation

_SYSTEM = (
    "You are a senior Python engineer. You receive a failing "
    "harness report and the source of one file. Return ONLY the "
    "corrected source for that file. No markdown fences. No prose. "
    "Preserve the public API — same functions, same classes."
)


def _prompt(target: str, source: str, obs: Observation) -> str:
    failures = obs.failures()[:8]
    report = {
        "harness": obs.harness,
        "mean": round(obs.mean, 4),
        "axis_pass": obs.axis_pass,
        "n": obs.n,
        "sample_failures": failures,
    }
    return (
        "Harness report:\n"
        + json.dumps(report, indent=2)
        + "\n\nFile: " + target + "\n\nSource:\n"
        + source
    )


def propose(target: str, source: str, obs: Observation,
            swarm) -> str:
    p = _prompt(target, source, obs)
    r = swarm.run_one(0, p, system=_SYSTEM, max_tokens=2048)
    text = r.text.strip()
    # drop any fences the model added despite instruction
    import re
    m = re.search(r"```[a-zA-Z]*\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    return text
