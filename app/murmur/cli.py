from __future__ import annotations

import argparse
import json
import sys

from app.murmur.connectors import by_category, list_tools
from app.murmur.flock import Flock


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="murmur")
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--ticks", type=int, default=50)
    p.add_argument("--dt", type=float, default=0.05)
    p.add_argument("--tool", default=None,
                   help="route act.* to this connector")
    p.add_argument("--list", action="store_true",
                   help="list all connectors")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    if a.list:
        print(json.dumps(by_category(), indent=2))
        print(f"\n  total: {len(list_tools())} tools")
        return 0

    flock = Flock(n=a.n)
    last = None
    for _ in range(a.ticks):
        last = flock.tick(dt=a.dt, tool=a.tool)

    if a.json:
        print(json.dumps(last, indent=2))
    else:
        print(f"  flock: {a.n} agents, {a.ticks} ticks, dt={a.dt}s")
        print(f"  tool : {a.tool or 'local'}")
        print()
        m = last["metrics"] if last else {}
        for k, v in m.items():
            print(f"  {k:20s} {v}")
        print()
        print("  sample effects:")
        for e in (last["effects"] if last else [])[:4]:
            print(f"    {e['agent']:6s} sit={e['situation']:9s} "
                  f"fc={e['forecast']:9s} dec={e['decision']:14s} "
                  f"ok={e['effect']} alloc={e['alloc_share']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
