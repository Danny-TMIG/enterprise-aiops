"""Print everything that fails to parse, for one prompt."""
from __future__ import annotations

import ast
import sys

from app.origami.dispatch import dispatch
from app.origami.library import get as get_grammar
from app.origami.swarm import Swarm


def main() -> int:
    swarm = Swarm(n_workers=1)
    grammar = get_grammar("rich_module")
    r = dispatch(grammar, swarm, intent="count the words in a string",
                 seed=0, max_depth=10, max_tokens=128)

    print("── leaves ──")
    for leaf in r.tree.get("leaves", []):
        pass  # tree doesn't carry leaves; use r.text instead
    for line in r.text.splitlines():
        print("  " + line[:120])
    print()

    print("── sections ──")
    for name in sorted(r.sections or {}):
        sec = r.sections[name]
        print(f"  [{name}]")
        if isinstance(sec, list):
            for i, item in enumerate(sec):
                print(f"    [{i}] {repr(item)[:240]}")
        elif isinstance(sec, dict):
            for k, v in sec.items():
                print(f"    {k}: {repr(v)[:240]}")
        else:
            print(f"    {repr(sec)[:240]}")
    print()
    print("── glued code ──")
    print(r.code if r.code else "<empty>")
    print()

    print("── cocycle ──")
    print(f"  ok        : {r.cocycle_ok}")
    for v in (r.violations or []):
        print(f"  violation : {v}")
    print()

    print("── parse ──")
    if not r.code:
        print("  empty")
        return 1
    try:
        ast.parse(r.code)
        print("  ok")
        return 0
    except SyntaxError as e:
        print(f"  line {e.lineno} col {e.offset}: {e.msg}")
        lines = r.code.splitlines()
        for i in range(max(0, (e.lineno or 1) - 3),
                       min(len(lines), (e.lineno or 1) + 2)):
            mark = ">>" if (i + 1) == e.lineno else "  "
            print(f"  {mark} {i+1:3d} | {lines[i]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
