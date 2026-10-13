"""Emit the harder training set."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.delta.delta import Delta
from app.delta.filter import filter_delta


def _h(*p: str) -> str:
    m = hashlib.sha256()
    for s in p:
        m.update(s.encode("utf-8")); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()[:24]


@dataclass
class SFTPair:
    prompt: str
    completion: str
    source_teacher: str
    source_student: str
    workload_id: str
    verifier_id: str
    verifier_evidence: str
    input_repr: str
    emitted_at: str = field(default_factory=lambda: time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    @property
    def id(self) -> str:
        return _h("sft", self.prompt, self.completion,
                  self.source_teacher, self.verifier_evidence)


@dataclass
class DPOPair:
    prompt: str
    chosen: str
    rejected: str
    source_teacher: str
    source_student: str
    workload_id: str
    verifier_id: str
    input_repr: str
    emitted_at: str = field(default_factory=lambda: time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    @property
    def id(self) -> str:
        return _h("dpo", self.prompt, self.chosen, self.rejected,
                  self.source_teacher)


class CurriculumWriter:
    def __init__(self, root: str = ".delta"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.sft_path = self.root / "sft.jsonl"
        self.dpo_path = self.root / "dpo.jsonl"
        self.rejected_path = self.root / "rejected.jsonl"
        for p in (self.sft_path, self.dpo_path, self.rejected_path):
            p.touch(exist_ok=True)

    def emit(self, deltas: list[Delta],
             workloads_by_id: dict[str, Any]) -> dict[str, int]:
        sft_n = dpo_n = rej_n = 0
        for d in deltas:
            workload = workloads_by_id.get(d.workload_id)
            if workload is None:
                continue
            decision = filter_delta(d, workload)
            if not decision.accept:
                self._append(self.rejected_path, {
                    "workload_id": d.workload_id,
                    "quadrant": d.quadrant.value,
                    "reason": decision.reason,
                })
                rej_n += 1
                continue

            teacher = d.teacher
            student = d.student

            sft = SFTPair(
                prompt=d.prompt, completion=teacher.output,
                source_teacher=teacher.model_id,
                source_student=student.model_id,
                workload_id=d.workload_id,
                verifier_id=teacher.verifier_id,
                verifier_evidence=teacher.verdict_evidence,
                input_repr=repr(d.input_value)[:120],
            )
            self._append(self.sft_path, self._to_dict(sft, "sft"))
            sft_n += 1

            dpo = DPOPair(
                prompt=d.prompt, chosen=teacher.output,
                rejected=student.output,
                source_teacher=teacher.model_id,
                source_student=student.model_id,
                workload_id=d.workload_id,
                verifier_id=teacher.verifier_id,
                input_repr=repr(d.input_value)[:120],
            )
            self._append(self.dpo_path, self._to_dict(dpo, "dpo"))
            dpo_n += 1

        return {"sft": sft_n, "dpo": dpo_n, "rejected": rej_n}

    def _to_dict(self, obj, kind: str) -> dict[str, Any]:
        d = asdict(obj); d["kind"] = kind; d["id"] = obj.id
        return d

    def _append(self, path: Path, obj: dict[str, Any]) -> None:
        with path.open("a") as f:
            f.write(json.dumps(obj) + "\n")
