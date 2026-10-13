"""meta CLI — human-gated self-modification."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.meta.loop import iterate


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="meta")
    p.add_argument("--target", default="app/origami/dispatch.py")
    p.add_argument("--harness", default="usefulness")
    p.add_argument("--max-iters", type=int, default=3)
    p.add_argument("--auto", default=None,
                   choices=[None, "accept", "reject", "edit"],
                   help="bypass prompt (for testing)")
    p.add_argument("--root", default=".")
    a = p.parse_args(argv)

    target_path = Path(a.root) / a.target
    if not target_path.exists():
        print(f"  target not found: {target_path}", file=sys.stderr)
        return 1

    print(f"── meta loop: {a.target} ──")
    print(f"  harness:    {a.harness}")
    print(f"  max iters:  {a.max_iters}")
    print(f"  auto:       {a.auto or 'interactive'}")
    print()

    results = iterate(
        target=a.target, harness=a.harness,
        max_iters=a.max_iters, auto=a.auto, root=a.root,
    )

    print()
    print("── summary ──")
    for r in results:
        mark = "ACCEPT" if r.accepted else "REJECT"
        b = r.before.get("mean") if r.before else "—"
        af = r.after.get("mean") if r.after else "—"
        print(f"  [{mark}] iter {r.iteration} "
              f"reason={r.reason}  {b} → {af}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
