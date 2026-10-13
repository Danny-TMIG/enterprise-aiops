"""Observer — run a harness, parse its structured output."""
from __future__ import annotations

import contextlib
import importlib
import io
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

_AXIS_NAMES = [
    "parses", "intent_match", "body_nonstub",
    "test_present", "no_undefined", "no_placeholders",
]
_USEFUL_RE = re.compile(
    r"^\s+\[(\d{6})\]\s+(.+?)\s+score=([\d.]+)\s*$", re.MULTILINE)
_SAFE_RE = re.compile(
    r"^\s+\[(SAFE|UNSAFE)\s*\]\s+(.+?)\s+violations=(\d+)\s*$",
    re.MULTILINE)


@dataclass
class Run:
    input: str
    bits: list[int]
    score: float


@dataclass
class Observation:
    harness: str
    ts: str
    runs: list[Run]
    axis_pass: dict[str, int]
    n: int
    raw: str = ""

    @property
    def mean(self) -> float:
        return sum(r.score for r in self.runs) / max(1, len(self.runs))

    @property
    def all_pass(self) -> bool:
        return all(all(b == 1 for b in r.bits) for r in self.runs)

    def failures(self) -> list[dict[str, Any]]:
        out = []
        for r in self.runs:
            bad = [_AXIS_NAMES[i] for i, b in enumerate(r.bits) if b == 0]
            if bad:
                out.append({"input": r.input, "failing_axes": bad,
                            "score": r.score})
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "harness": self.harness, "ts": self.ts, "n": self.n,
            "mean": round(self.mean, 4), "all_pass": self.all_pass,
            "axis_pass": self.axis_pass,
            "failures": self.failures(),
        }


def _capture(mod) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            mod.main()
        except SystemExit:
            pass
    return buf.getvalue()


def _observe_usefulness() -> Observation:
    mod = importlib.import_module("app.proof.usefulness")
    raw = _capture(mod)
    runs: list[Run] = []
    for bits_s, prompt, score_s in _USEFUL_RE.findall(raw):
        runs.append(Run(
            input=prompt.strip(),
            bits=[int(c) for c in bits_s],
            score=float(score_s),
        ))
    axis_pass = {name: 0 for name in _AXIS_NAMES}
    for r in runs:
        for i, b in enumerate(r.bits):
            if b == 1:
                axis_pass[_AXIS_NAMES[i]] += 1
    return Observation(
        harness="usefulness",
        ts=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        runs=runs, axis_pass=axis_pass, n=len(runs), raw=raw,
    )


def observe_usefulness() -> Observation:  # type: ignore[no-redef]
    return _observe_usefulness()


def observe_murmur() -> Observation:
    mod = importlib.import_module("app.proof.murmur_proof")
    raw = _capture(mod)
    # reuse the usefulness line regex — same shape
    runs: list[Run] = []
    for bits_s, name, score_s in _USEFUL_RE.findall(raw):
        runs.append(Run(input=name.strip(),
                        bits=[int(c) for c in bits_s],
                        score=float(score_s)))
    axis_names = ["effect_ok", "recentered", "aligned",
                  "verdict_ok", "reinforced", "not_capped"]
    axis_pass = {a: 0 for a in axis_names}
    for r in runs:
        for i, b in enumerate(r.bits):
            if b == 1:
                axis_pass[axis_names[i]] += 1
    return Observation(
        harness="murmur",
        ts=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        runs=runs, axis_pass=axis_pass, n=len(runs), raw=raw,
    )


def observe(harness: str = "usefulness") -> Observation:
    if harness == "usefulness":
        return _observe_usefulness()
    if harness == "murmur":
        return observe_murmur()
    raise ValueError(f"unknown harness: {harness}")
