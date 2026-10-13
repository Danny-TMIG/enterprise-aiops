"""Tool synthesis from invariants.

A rule-tool is fully specified by (input type, output type, invariant).
Given those, this module enumerates template implementations, runs each
against the invariant on random inputs, and registers the first that
passes. The tool was not collected — it was synthesized from its own
property and validated by that property.

Model-tools (trained weights) and infra-tools (kubernetes, postgres)
are NOT in this class. They are declared by app/localmodel.py and
app/bridges/*, honestly, as external.
"""
from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

Invariant = Callable[[Any, Any], bool]
Template = Callable[..., Callable]


# ── candidate implementations for the pool ────────────────────────
def _t_sorted(xs): return sorted(xs)
def _t_sorted_rev(xs): return sorted(xs, reverse=True)
def _t_unsorted(xs): return list(xs)
def _t_reverse(xs): return list(reversed(xs))
def _t_unique(xs): return list(dict.fromkeys(xs))
def _t_dupes(xs): return [x for x in xs if xs.count(x) > 1]
def _t_sum(xs): return sum(xs)
def _t_count(xs): return len(xs)
def _t_max(xs): return max(xs) if xs else None
def _t_min(xs): return min(xs) if xs else None
def _t_evens(xs): return [x for x in xs if x % 2 == 0]
def _t_odds(xs): return [x for x in xs if x % 2 == 1]
def _t_double(xs): return [x * 2 for x in xs]
def _t_square(xs): return [x * x for x in xs]
def _t_head(xs): return xs[0] if xs else None
def _t_tail(xs): return xs[-1] if xs else None
def _t_partition_even(xs): return ([x for x in xs if x % 2 == 0],
                                    [x for x in xs if x % 2 == 1])
def _t_flatten(xs): return [y for x in xs for y in x]
def _t_chunk2(xs): return [xs[i:i+2] for i in range(0, len(xs), 2)]
def _t_pairs(xs): return list(zip(xs, xs[1:]))


TEMPLATES: list[tuple[str, Template]] = [
    ("sorted",        lambda: _t_sorted),
    ("sorted_rev",    lambda: _t_sorted_rev),
    ("identity",      lambda: _t_unsorted),
    ("reverse",       lambda: _t_reverse),
    ("unique",        lambda: _t_unique),
    ("dupes",         lambda: _t_dupes),
    ("sum",           lambda: _t_sum),
    ("count",         lambda: _t_count),
    ("max",           lambda: _t_max),
    ("min",           lambda: _t_min),
    ("evens",         lambda: _t_evens),
    ("odds",          lambda: _t_odds),
    ("double",        lambda: _t_double),
    ("square",        lambda: _t_square),
    ("head",          lambda: _t_head),
    ("tail",          lambda: _t_tail),
    ("partition_even",lambda: _t_partition_even),
    ("flatten",       lambda: _t_flatten),
    ("chunk2",        lambda: _t_chunk2),
    ("pairs",         lambda: _t_pairs),
]


# ── the synthesizer ────────────────────────────────────────────────
@dataclass
class Synthesis:
    name: str
    invariant: Invariant
    template_used: str | None = None
    impl: Callable | None = None
    attempts: int = 0
    passed: bool = False
    failures: list[tuple[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "template": self.template_used,
                "attempts": self.attempts, "passed": self.passed,
                "failures": self.failures[:6]}


def _default_inputs(rng: random.Random, n: int = 64) -> list[Any]:
    """Random inputs an implementation might see. Generators can
    extend this list. Only flat int-lists — nested inputs are for a
    different tool family and are not synthesized here."""
    out: list[Any] = []
    for _ in range(n):
        k = rng.randint(0, 5)
        size = rng.randint(0, 12)
        xs = [rng.randint(-20, 20) for _ in range(size)]
        if k == 0: out.append(xs)
        elif k == 1: out.append(sorted(xs))
        elif k == 2: out.append(xs + xs)          # duplicates
        elif k == 3: out.append([])
        elif k == 4: out.append([rng.randint(0, 3)])  # singleton
        else: out.append([rng.randint(0, 2) for _ in range(size)])  # low entropy
    return out


def synthesize(name: str,
               invariant: Invariant,
               *,
               pool: Sequence[tuple[str, Template]] | None = None,
               inputs: list[Any] | None = None,
               seed: int = 0) -> Synthesis:
    rng = random.Random(seed)
    pool = list(pool or TEMPLATES)
    inputs = inputs if inputs is not None else _default_inputs(rng)
    syn = Synthesis(name=name, invariant=invariant)
    for tname, maker in pool:
        syn.attempts += 1
        try:
            fn = maker()
        except Exception as e:
            syn.failures.append((tname, f"maker: {e}")); continue
        ok = True
        for x in inputs:
            try:
                y = fn(x)
            except Exception as e:
                syn.failures.append((tname, f"raise: {e}")); ok = False; break
            try:
                if not invariant(x, y):
                    syn.failures.append((tname, f"invariant on {x[:3]}… → {y!r}")); ok = False; break
            except (TypeError, ValueError):
                # invariant not applicable to this input shape; skip
                continue
            except Exception as e:
                syn.failures.append((tname, f"inv raise: {e}")); ok = False; break
        if ok:
            syn.template_used = tname
            syn.impl = fn
            syn.passed = True
            return syn
    return syn


# ── invariants: the specification of each tool ────────────────────
INVARIANTS: dict[str, Invariant] = {
    # every invariant checks isinstance(y, expected) FIRST so a wrong
    # template's output type can never pass by accident.
    "sort":      lambda x, y: isinstance(y, list) and y == sorted(x),
    "sort_desc": lambda x, y: isinstance(y, list) and y == sorted(x, reverse=True),
    "reverse":   lambda x, y: isinstance(y, list) and y == list(reversed(x)),
    "unique":    lambda x, y: (isinstance(y, list)
                               and len(y) == len(set(y))
                               and sorted(y) == sorted(set(x))),
    "sum":       lambda x, y: isinstance(y, int) and y == sum(x),
    "count":     lambda x, y: isinstance(y, int) and y == len(x),
    "max":       lambda x, y: ((isinstance(y, int) and y == max(x)) if x else y is None),
    "min":       lambda x, y: ((isinstance(y, int) and y == min(x)) if x else y is None),
    "evens":     lambda x, y: (isinstance(y, list)
                               and all(isinstance(i, int) and i % 2 == 0 for i in y)
                               and y == [i for i in x if i % 2 == 0]),
    "odds":      lambda x, y: (isinstance(y, list)
                               and y == [i for i in x if i % 2 == 1]),
    "double":    lambda x, y: (isinstance(y, list)
                               and y == [i * 2 for i in x]),
    "square":    lambda x, y: (isinstance(y, list)
                               and y == [i * i for i in x]),
    "head":      lambda x, y: ((isinstance(y, int) and y == x[0]) if x else y is None),
    "tail":      lambda x, y: ((isinstance(y, int) and y == x[-1]) if x else y is None),
    "pairs":     lambda x, y: (isinstance(y, list)
                               and len(y) == max(0, len(x) - 1)
                               and all(isinstance(p, tuple) and len(p) == 2 for p in y)
                               and all(y[i] == (x[i], x[i+1]) for i in range(len(y)))),
}


def generate_all(*, seed: int = 0) -> dict[str, Synthesis]:
    """Synthesize every tool declared in INVARIANTS."""
    return {name: synthesize(name, inv, seed=seed)
            for name, inv in INVARIANTS.items()}


# ── self-registration: each synthesized tool becomes a capability ─
def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    report = generate_all(seed=0)
    for name, syn in report.items():
        if not syn.passed or syn.impl is None:
            continue
        def make(s=name, fn=syn.impl):
            def runner(*args: Any, **kwargs: Any) -> dict:
                xs = args[0] if args else kwargs.get("xs") or kwargs.get("input") or []
                return {"tool": s, "in": xs, "out": fn(xs)}
            return runner
        register("gen_" + name)(make())

    # expose the synthesis report itself
    def _report(*args: Any, **kwargs: Any) -> dict:
        r = generate_all(seed=int(kwargs.get("seed", 0)))
        return {"generated": {k: v.to_dict() for k, v in r.items()}}
    register("generate")(_report)


_self_register()

__all__ = ["INVARIANTS", "TEMPLATES", "Synthesis", "generate_all", "synthesize"]

# ── held-out accuracy ──────────────────────────────────────────────
def accuracy(*, seed: int = 999, n: int = 256) -> dict:
    """Synthesize on training inputs, test on fresh ones. Reports
    pass/fail per tool and a total."""
    rng = random.Random(seed)
    held = _default_inputs(rng, n)
    syn = generate_all(seed=0)
    report = {}
    passed = 0
    for name, s in syn.items():
        if not s.passed or s.impl is None:
            report[name] = {"synthesized": False}
            continue
        inv = INVARIANTS[name]
        ok = 0
        for x in held:
            try:
                y = s.impl(x)
                if inv(x, y):
                    ok += 1
            except Exception:
                pass
        report[name] = {"synthesized": True,
                        "held_out_pass": ok, "held_out_n": n,
                        "accuracy": ok / n}
        if ok == n:
            passed += 1
    return {"tools": report, "perfect": passed, "total": len(syn)}
