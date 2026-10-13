"""Self-contained verifiable workloads for the delta pipeline.

No dependency on app.dominion. Same shape as dominion workloads
but defined here so the delta module runs standalone.
"""
from __future__ import annotations

import ast
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# ── verdict ─────────────────────────────────────────────────────
PASS = "PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"
ERROR = "ERROR"


@dataclass
class Verdict:
    state: str
    verifier_id: str
    evidence: str = ""

    @property
    def passed(self) -> bool:
        return self.state == PASS


# ── extractors ──────────────────────────────────────────────────
def _extract(name: str):
    def extract(text: str):
        t = text.strip()
        if t.startswith("```"):
            t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
            t = re.sub(r"\n?```\s*$", "", t)
        ns: dict[str, Any] = {}
        exec(compile(ast.parse(t), "<cand>", "exec"), ns)
        if name not in ns:
            raise NameError(f"{name!r} not found")
        return ns[name]
    return extract


# ── workload ────────────────────────────────────────────────────
@dataclass
class Workload:
    id: str
    prompt: str
    verifier: Any
    description: str = ""


# ── verifiers ───────────────────────────────────────────────────
@dataclass
class DifferentialVerifier:
    id: str
    reference: Callable[[Any], Any]
    fixtures: list[Any]
    extract: Callable[[str], Callable[[Any], Any]]
    equality: Callable[[Any, Any], bool] = lambda a, b: a == b

    def verify(self, input_value: Any, output_text: str) -> Verdict:
        try:
            cand = self.extract(output_text)
        except Exception as e:
            return Verdict(FAIL, self.id, f"extract: {e}")
        for fix in self.fixtures:
            try:
                want = self.reference(fix)
                got = cand(fix)
            except Exception as e:
                return Verdict(FAIL, self.id, f"raised on {fix!r}: {e}")
            if not self.equality(got, want):
                return Verdict(FAIL, self.id,
                               f"mismatch on {fix!r}: {got!r} != {want!r}")
        return Verdict(PASS, self.id, f"{len(self.fixtures)} fixtures match")


# ── reference implementations ───────────────────────────────────
def _ref_count_words(s): return len(str(s).split())
def _ref_reverse_list(xs): return list(reversed(list(xs)))
def _ref_is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
def _ref_sum_list(xs): return sum(xs)
def _ref_parse_env_int(raw):
    return int(str(raw).replace("_", "").replace(",", ""))


WORKLOADS: dict[str, Workload] = {
    "count_words": Workload(
        "count_words",
        "Write a Python function `count_words(s: str) -> int` that "
        "returns the number of whitespace-separated words. Only the "
        "function, no markdown.",
        DifferentialVerifier(
            id="diff.count_words",
            reference=_ref_count_words,
            fixtures=["", "hello", "hello world", "a b c d e"],
            extract=_extract("count_words"),
        )),
    "reverse_list": Workload(
        "reverse_list",
        "Write a Python function `reverse_list(xs)` returning the "
        "list reversed. Only the function.",
        DifferentialVerifier(
            id="diff.reverse_list",
            reference=_ref_reverse_list,
            fixtures=[[], [1], [1, 2, 3], ["a", "b", "c"]],
            extract=_extract("reverse_list"),
            equality=lambda a, b: list(a) == list(b),
        )),
    "is_prime": Workload(
        "is_prime",
        "Write a Python function `is_prime(n: int) -> bool` returning "
        "True iff n is prime. Only the function.",
        DifferentialVerifier(
            id="diff.is_prime",
            reference=_ref_is_prime,
            fixtures=[-3, 0, 1, 2, 3, 4, 17, 25, 97],
            extract=_extract("is_prime"),
            equality=lambda a, b: bool(a) == bool(b),
        )),
    "sum_list": Workload(
        "sum_list",
        "Write a Python function `sum_list(xs)` returning the sum. "
        "Only the function.",
        DifferentialVerifier(
            id="diff.sum_list",
            reference=_ref_sum_list,
            fixtures=[[], [0], [1, 2, 3], list(range(10))],
            extract=_extract("sum_list"),
        )),
    "parse_env_int": Workload(
        "parse_env_int",
        "Write a Python function `parse_env_int(raw: str) -> int` "
        "that accepts '1', '1_000', '1,234'. Only the function.",
        DifferentialVerifier(
            id="diff.parse_env_int",
            reference=_ref_parse_env_int,
            fixtures=["1", "1_000", "1,234", "0", "-42"],
            extract=_extract("parse_env_int"),
        )),
}


def list_workloads() -> list[str]:
    return sorted(WORKLOADS)


def get(workload_id: str) -> Workload:
    if workload_id not in WORKLOADS:
        raise KeyError(f"unknown workload: {workload_id}")
    return WORKLOADS[workload_id]


# ── transchain workload ─────────────────────────────────────────
def _ref_zigzag(pair):
    a, b = pair
    out = []
    i = j = 0
    while i < len(a) or j < len(b):
        if i < len(a):
            out.append(a[i]); i += 1
        if j < len(b):
            out.append(b[j]); j += 1
    return out


def _extract_zigzag(text: str):
    fn = _extract("zigzag")(text)
    def wrapped(pair):
        a, b = pair
        return list(fn(a, b))
    return wrapped


WORKLOADS["chain_zigzag"] = Workload(
    "chain_zigzag",
    "Write a Python function `zigzag(a, b)` that takes two lists "
    "and returns their interleave: a[0], b[0], a[1], b[1], ... If "
    "one list is longer, append its remaining elements. Return only "
    "the function, no markdown.",
    DifferentialVerifier(
        id="diff.chain_zigzag",
        reference=_ref_zigzag,
        fixtures=[
            ([], []),
            (["A"], ["X"]),
            (["A", "B", "C"], ["X", "Y", "Z"]),
            (["A", "B", "C", "D"], ["X", "Y"]),
            (["A"], ["X", "Y", "Z"]),
        ],
        extract=_extract_zigzag,
        equality=lambda a, b: list(a) == list(b),
    ),
)
