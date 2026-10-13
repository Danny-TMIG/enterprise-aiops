"""Enterprise state machine."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LockError(RuntimeError): pass
class PolicyError(RuntimeError): pass

class State(str, Enum):
    INIT = "init"; READY = "ready"; RUNNING = "running"
    DEGRADED = "degraded"; HALTED = "halted"

_T = {
    State.INIT:     {State.READY, State.HALTED},
    State.READY:    {State.RUNNING, State.HALTED},
    State.RUNNING:  {State.DEGRADED, State.READY, State.HALTED},
    State.DEGRADED: {State.RUNNING, State.HALTED},
    State.HALTED:   set(),
}

@dataclass
class EnterpriseStateMachine:
    state: State = State.INIT
    locked: bool = False
    history: list[State] = field(default_factory=list)
    def __post_init__(self): self.history.append(self.state)
    def lock(self): self.locked = True
    def unlock(self): self.locked = False
    def transition(self, target: State, *, policy_ok: bool = True) -> State:
        if self.locked: raise LockError(f"locked: {self.state} -> {target}")
        if not policy_ok: raise PolicyError(f"policy: {self.state} -> {target}")
        if target not in _T.get(self.state, set()):
            raise PolicyError(f"illegal: {self.state} -> {target}")
        self.state = target; self.history.append(target); return target
    def can(self, target): return not self.locked and target in _T.get(self.state, set())
    def reset(self): self.state = State.INIT; self.history = [State.INIT]; self.locked = False
