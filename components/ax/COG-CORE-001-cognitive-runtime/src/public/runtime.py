"""COG-CORE-001 — Cognitive Runtime (full).

Operates the cognitive lifecycle over a replaceable substrate. Records
stage checkpoints; returns typed outcomes; substrate swaps do not change
the runtime interface.
"""
from __future__ import annotations
import time, uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CognitiveCheckpoint:
    checkpoint_id: str; operation_id: str; stage: str
    state: Dict[str, Any]; created_at: float


@dataclass
class OperationOutcome:
    operation_id: str; substrate: str; result: Any = None
    failure: Optional[str] = None
    checkpoints: List[CognitiveCheckpoint] = field(default_factory=list)

    def stages(self) -> List[str]:
        return [c.stage for c in self.checkpoints]


class CognitiveRuntime:
    STAGES = ("receive", "represent", "route", "reason", "evaluate", "seal")

    def __init__(self, model_name: str = "mlx-community/Qwen2.5-7B-Instruct-4bit"):
        self.model_name = model_name
        self._ops: Dict[str, OperationOutcome] = {}

    def _ckpt(self, op: OperationOutcome, stage: str, state: Dict[str, Any]) -> None:
        op.checkpoints.append(CognitiveCheckpoint(
            f"ckpt-{uuid.uuid4().hex[:8]}", op.operation_id, stage, state, time.time()
        ))

    def begin(self, prompt: str) -> OperationOutcome:
        if not prompt or not prompt.strip():
            raise ValueError("prompt required")
        op = OperationOutcome(f"op-{uuid.uuid4().hex[:12]}", self.model_name)
        self._ckpt(op, "receive", {"prompt": prompt})
        self._ckpt(op, "represent", {"substrate": self.model_name})
        self._ops[op.operation_id] = op
        return op

    def execute(self, op_id: str, prompt: str) -> str:
        op = self._ops.get(op_id)
        if op is None:
            raise ValueError(f"unknown operation {op_id}")
        self._ckpt(op, "route", {"target": "local"})
        self._ckpt(op, "reason", {"substrate": op.substrate})
        op.result = f"[{op.substrate}] {prompt}"
        self._ckpt(op, "evaluate", {"result_len": len(op.result)})
        return op.result

    def finish(self, op_id: str, failure: Optional[str] = None) -> OperationOutcome:
        op = self._ops.get(op_id)
        if op is None:
            raise ValueError(f"unknown operation {op_id}")
        op.failure = failure
        self._ckpt(op, "seal", {"failure": failure})
        return op

    def get(self, op_id: str) -> OperationOutcome:
        op = self._ops.get(op_id)
        if op is None:
            raise ValueError(f"unknown operation {op_id}")
        return op
