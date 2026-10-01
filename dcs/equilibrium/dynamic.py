"""Dynamic equilibrium: measure → delta → generate → converge.

Nothing is fixed. The floor is derived. Requirements are generated
from parametrized templates keyed by hat and index. Each step is
recorded as a trajectory point. The controller stops when either:

    - all deltas are zero (converged)
    - a max-step budget is exhausted (bounded)
    - no template can produce a new requirement for a hat (stuck)

Every state transition is signed.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field

from dcs.equilibrium.templates import TEMPLATES
from dcs.hats import HATS
from dcs.standard import Requirement, Standard


# ── state ─────────────────────────────────────────────────────────
@dataclass
class HatState:
    code: str
    count: int
    delta: int  # floor - count (0 means at/above)
    used_templates: int


@dataclass
class Step:
    index: int
    ts: float
    floor: int
    per_hat: dict[str, HatState]
    added: list[str] = field(default_factory=list)  # requirement ids added
    digest: str = ""

    def to_dict(self):
        return {
            "index": self.index,
            "ts": self.ts,
            "floor": self.floor,
            "per_hat": {k: asdict(v) for k, v in self.per_hat.items()},
            "added": self.added,
            "digest": self.digest,
        }


# ── measurement ───────────────────────────────────────────────────
def measure(std: Standard, floor: int) -> dict[str, HatState]:
    counts = dict.fromkeys(HATS, 0)
    for r in std.requirements:
        for h in r.hats:
            if h in counts:
                counts[h] += 1
    return {
        h: HatState(code=h, count=counts[h], delta=max(0, floor - counts[h]), used_templates=0)
        for h in HATS
    }


def derive_floor(std: Standard, *, multiplier: float = 0.0, minimum: int = 8) -> int:
    """Floor = max(minimum, ceil(multiplier * median_hat_count)).
    Default multiplier 0 means floor is just minimum; controller escalates."""
    counts = sorted(sum(1 for r in std.requirements if h in r.hats) for h in HATS)
    median = counts[len(counts) // 2]
    return max(minimum, int(median * multiplier) if multiplier else minimum)


# ── generation ────────────────────────────────────────────────────
class RequirementGenerator:
    """Wraps templates so each generated requirement is unique by (hat, n)."""

    def __init__(self, seed: int = 0):
        self.seed = seed
        self._used: set[str] = set()

    def for_hat(self, hat: str) -> Requirement | None:
        if hat not in TEMPLATES:
            return None
        fn = TEMPLATES[hat]
        for i in range(64):
            rid = f"EQ-{hat}-{self._instance(hat, i):03d}"
            if rid in self._used:
                continue
            r = fn(rid, i + self.seed)
            if r is None:
                continue
            self._used.add(rid)
            return r
        return None

    def _instance(self, hat: str, i: int) -> int:
        return hash((hat, self.seed, i)) % 1000


# ── controller ────────────────────────────────────────────────────
def step(std: Standard, floor: int, gen: RequirementGenerator, index: int) -> tuple[Standard, Step]:
    """One cycle: measure, generate one requirement per unsatisfied hat."""
    per_hat = measure(std, floor)
    added: list[str] = []

    existing = list(std.requirements)
    for hat, state in per_hat.items():
        if state.delta <= 0:
            continue
        r = gen.for_hat(hat)
        if r is None:
            continue
        existing.append(r)
        added.append(r.id)
        state.used_templates += 1

    new_std = Standard(
        id=std.id,
        version=std.version,
        title=std.title,
        published=std.published,
        authority=std.authority,
        requirements=existing,
    )
    st = Step(
        index=index,
        ts=time.time(),
        floor=floor,
        per_hat=measure(new_std, floor),
        added=added,
    )
    st.digest = _digest(st)
    return new_std, st


def converge(
    std: Standard,
    *,
    floor: int = 12,
    max_steps: int = 200,
    seed: int = 0,
    trace: list[Step] | None = None,
) -> tuple[Standard, list[Step]]:
    gen = RequirementGenerator(seed)
    steps: list[Step] = []
    cur = std
    for i in range(max_steps):
        cur, st = step(cur, floor, gen, i)
        steps.append(st)
        if not st.added:
            break
    if trace is not None:
        trace.extend(steps)
    return cur, steps


def _digest(st: Step) -> str:
    payload = json.dumps(
        {
            "index": st.index,
            "floor": st.floor,
            "added": st.added,
            "per_hat": {k: v.count for k, v in st.per_hat.items()},
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()[:16]


# ── reporting ─────────────────────────────────────────────────────
def render_step(st: Step) -> str:
    lines = [
        f"step {st.index:02d}  floor={st.floor}  added={len(st.added)}  digest={st.digest}",
    ]
    need = sum(v.delta for v in st.per_hat.values())
    at = sum(1 for v in st.per_hat.values() if v.delta == 0)
    lines.append(f"  hats at floor: {at}/{len(st.per_hat)}  total need: {need}")
    if st.added:
        lines.append(f"  new: {', '.join(st.added[:8])}" + (" ..." if len(st.added) > 8 else ""))
    return "\n".join(lines)


def render_trace(steps: list[Step]) -> str:
    lines = [f"trace: {len(steps)} step(s)"]
    for st in steps:
        lines.append(render_step(st))
    return "\n".join(lines)


def render_equilibrium(std: Standard, floor: int) -> str:
    per = measure(std, floor)
    at = sum(1 for v in per.values() if v.delta == 0)
    need = sum(v.delta for v in per.values())
    lines = [
        f"equilibrium (floor={floor})",
        "=" * 40,
        f"hats at floor: {at}/{len(per)}",
        f"requirements needed: {need}",
        "",
        "Per hat:",
    ]
    for h in sorted(per):
        v = per[h]
        bar = "●" * min(v.count, 30)
        flag = "" if v.delta == 0 else f"  +{v.delta}"
        lines.append(f"  {h:<5} {HATS[h]:<18} {v.count:>3}{flag:<6} {bar}")
    return "\n".join(lines)
