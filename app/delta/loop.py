"""Run cycles. Two local models. No network. No third-party teacher."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.delta.curriculum import CurriculumWriter
from app.delta.delta import Delta, delta_set, summarize
from app.delta.model import Model
from app.delta.probe import Probe, run_probe


@dataclass
class Cycle:
    index: int
    probes_a: list[Probe]
    probes_b: list[Probe]
    deltas: list[Delta]
    summary: dict[str, int]
    emitted: dict[str, int]


@dataclass
class LoopState:
    cycles: list[Cycle] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"cycles": [
            {"index": c.index, "summary": c.summary, "emitted": c.emitted}
            for c in self.cycles
        ]}


def run_cycle(index: int, models: dict[str, Model], workloads: list[Any],
              inputs: dict[str, Any], writer: CurriculumWriter,
              seed: int = 0, model_a: str = "A",
              model_b: str = "B") -> Cycle:
    a = models[model_a]; b = models[model_b]
    pa, pb = [], []
    for w in workloads:
        inp = inputs.get(w.id, w.id)
        pa.append(run_probe(a, w, inp, seed))
        pb.append(run_probe(b, w, inp, seed))
    deltas = delta_set(pa, pb)
    summary = summarize(deltas)
    wl_by_id = {w.id: w for w in workloads}
    emitted = writer.emit(deltas, wl_by_id)
    return Cycle(index=index, probes_a=pa, probes_b=pb,
                 deltas=deltas, summary=summary, emitted=emitted)


def run_loops(n: int, models: dict[str, Model], workloads: list[Any],
              inputs: dict[str, Any],
              writer: CurriculumWriter | None = None,
              seed: int = 0, model_a: str = "A",
              model_b: str = "B") -> LoopState:
    writer = writer or CurriculumWriter()
    state = LoopState()
    for i in range(n):
        state.cycles.append(run_cycle(i, models, workloads, inputs,
                                      writer, seed=seed,
                                      model_a=model_a, model_b=model_b))
    return state
