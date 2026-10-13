"""Run one model against one workload. Record the outcome."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

from app.delta.model import Model


@dataclass
class Probe:
    model_id: str
    workload_id: str
    input_value: Any
    prompt: str
    output: str
    verdict_state: str
    verdict_evidence: str
    verifier_id: str
    duration_ms: float = 0.0

    @property
    def passed(self) -> bool:
        return self.verdict_state == "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "workload_id": self.workload_id,
            "input_value": repr(self.input_value)[:80],
            "output_hash": hashlib.sha256(
                self.output.encode()).hexdigest()[:16],
            "verdict": self.verdict_state,
            "verifier": self.verifier_id,
            "evidence": self.verdict_evidence[:120],
        }


def run_probe(model: Model, workload, input_value: Any,
              seed: int = 0) -> Probe:
    t0 = time.time()
    try:
        output = model.generate(workload.prompt, seed)
    except Exception as e:
        output = f"<error:{type(e).__name__}:{e}>"
    v = workload.verifier.verify(input_value, output)
    return Probe(
        model_id=model.id,
        workload_id=workload.id,
        input_value=input_value,
        prompt=workload.prompt,
        output=output,
        verdict_state=v.state,
        verdict_evidence=v.evidence,
        verifier_id=v.verifier_id,
        duration_ms=(time.time() - t0) * 1000.0,
    )
