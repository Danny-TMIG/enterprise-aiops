"""Demo the delta pipeline against the dominion workloads."""
from __future__ import annotations

import json
import sys

from app.delta import workloads as wl
from app.delta.curriculum import CurriculumWriter
from app.delta.loop import run_loops
from app.delta.model import FixtureModel

A_FIXTURES = [
    ("count",   "def count_words(s):\n    return len(s.split())\n"),
    ("reverse", "def reverse_list(xs):\n    return list(reversed(xs))\n"),
    ("sum",     "def sum_list(xs):\n    return sum(xs)\n"),
    ("prime",   "def is_prime(n):\n    return n > 1\n"),
    ("env",     "def parse_env_int(raw):\n    return int(raw)\n"),
    ("zigzag",  "def zigzag(a, b):\n"
                "    out = []\n"
                "    i = j = 0\n"
                "    while i < len(a) or j < len(b):\n"
                "        if i < len(a): out.append(a[i]); i += 1\n"
                "        if j < len(b): out.append(b[j]); j += 1\n"
                "    return out\n"),
]

B_FIXTURES = [
    ("count",   "def count_words(s):\n    return len(s)\n"),
    ("reverse", "def reverse_list(xs):\n    return list(reversed(xs))\n"),
    ("sum",     "def sum_list(xs):\n    return len(xs)\n"),
    ("prime",
     "def is_prime(n):\n"
     "    if n < 2:\n        return False\n"
     "    i = 2\n"
     "    while i * i <= n:\n"
     "        if n % i == 0:\n            return False\n"
     "        i += 1\n"
     "    return True\n"),
    ("env",
     "def parse_env_int(raw):\n"
     "    return int(str(raw).replace('_','').replace(',',''))\n"),
]


def main() -> int:
    print("=" * 68)
    print("  delta pipeline - local models only, no network")
    print("=" * 68)
    print(f"  workloads: {wl.list_workloads()}")

    model_a = FixtureModel(id="A", fixtures=A_FIXTURES,
                           fallback="<A-no-op>")
    model_b = FixtureModel(id="B", fixtures=B_FIXTURES,
                           fallback="<B-no-op>")

    workloads = [wl.get(w) for w in ("count_words", "reverse_list",
                                     "is_prime", "sum_list",
                                     "parse_env_int", "chain_zigzag")]
    inputs = {w.id: w.id for w in workloads}

    writer = CurriculumWriter(root=".delta")
    state = run_loops(2, {"A": model_a, "B": model_b},
                      workloads, inputs, writer=writer)

    for c in state.cycles:
        print()
        print(f"-- cycle {c.index} --")
        print(f"  summary: {c.summary}")
        print(f"  emitted: {c.emitted}")
        for d in c.deltas:
            t = d.teacher.model_id if d.teacher else "-"
            s = d.student.model_id if d.student else "-"
            mark = "->" if d.is_signal else " ."
            print(f"   [{mark}] {d.workload_id:16s} "
                  f"{d.quadrant.value:12s} teacher={t} student={s}")

    print()
    print("-- curriculum written --")
    for p in (writer.sft_path, writer.dpo_path, writer.rejected_path):
        n = len(p.read_text().splitlines())
        print(f"  {p.name:16s} {n} lines")

    print()
    print("-- first SFT pair --")
    if writer.sft_path.read_text().strip():
        first = json.loads(writer.sft_path.read_text().splitlines()[0])
        print(f"  id:       {first['id']}")
        print(f"  teacher:  {first['source_teacher']}")
        print(f"  student:  {first['source_student']}")
        print(f"  verifier: {first['verifier_id']}")
        print(f"  evidence: {first['verifier_evidence'][:80]}")
        print(f"  prompt:   {first['prompt'][:80]}")
        print(f"  completion[:60]: {first['completion'][:60]!r}")

    print()
    print("  done. No network calls were made. The signal is the")
    print("  delta set filtered by the same verifier the compiler")
    print("  uses to emit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
