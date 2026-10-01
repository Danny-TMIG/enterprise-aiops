"""State — the smallest thing an agent carries between ticks."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Signal:
    source: str
    kind: str
    value: float
    payload: Dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


@dataclass
class Situation:
    label: str
    confidence: float
    deviation: float
    features: Dict[str, float] = field(default_factory=dict)


@dataclass
class Forecast:
    outcome: str
    probability: float
    risk: float
    horizon_s: float = 1.0


@dataclass
class Decision:
    verb: str
    params: Dict[str, Any] = field(default_factory=dict)
    urgency: float = 0.0


@dataclass
class Effect:
    verb: str
    ok: bool
    detail: str = ""
    tool: Optional[str] = None
    ts: float = field(default_factory=time.time)


@dataclass
class Coordination:
    peers: List[str] = field(default_factory=list)
    overlaps: int = 0
    delegates: List[str] = field(default_factory=list)


@dataclass
class Allocation:
    share: float = 1.0
    budget: float = 0.0
    cap_hit: bool = False


@dataclass
class Verdict:
    ok: bool
    delta: float = 0.0
    reason: str = ""


@dataclass
class Update:
    threshold: float = 0.0
    weight: float = 0.0
    reason: str = ""


@dataclass
class AgentState:
    agent_id: str
    position: Dict[str, float] = field(default_factory=dict)
    velocity: Dict[str, float] = field(default_factory=dict)
    baseline: Dict[str, float] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    last_effect: Optional[Effect] = None
    last_verdict: Optional[Verdict] = None
    ticks: int = 0
    last_tick_ts: float = field(default_factory=time.time)

    def deviation(self) -> float:
        total = 0.0
        for k, v in self.position.items():
            b = self.baseline.get(k, v)
            total += abs(v - b)
        return total
