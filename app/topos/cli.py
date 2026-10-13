from __future__ import annotations

import argparse
import json
import sys

from app.topos.runtime import ToposRuntime


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="topos")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    rt = ToposRuntime()
    st = rt.status()
    if a.json:
        print(json.dumps(st, indent=2, default=str))
    else:
        print(f"T  : {st['T']['objects']} objects, {st['T']['morphisms']} morphisms")
        print(f"Ω  : {st['T']['has_omega']}  1: {st['T']['has_terminal']}")
        print(f"axes: F={st['axes']['Forward']['objects']} "
              f"G={st['axes']['Inverse']['objects']} "
              f"R={st['axes']['Relational']['objects']}")
        print(f"self-similar: {st['self_similar']['verification']}")
        print(f"F ⊣ G: {st['adjunction']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
