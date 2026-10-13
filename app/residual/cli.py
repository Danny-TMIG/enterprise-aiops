"""Print the grounding of every module in the register."""
from __future__ import annotations

import json
import sys

from app.residual import register as R
from app.residual.anchors import validate
from app.residual.terminate import render, terminate_all


def main() -> int:
    print("═══════════════════════════════════════════════════════════════")
    print("  Residual Register — summary")
    print("═══════════════════════════════════════════════════════════════")
    rep = R.report()
    print(f"  total residuals:   {rep['total']}")
    print(f"  classes:           {rep['classes']}")
    print(f"  arity distribution: {rep['arity_distribution']}")
    print()
    print("  by class:")
    for cls, n in sorted(rep["by_class"].items(),
                        key=lambda kv: -kv[1]):
        print(f"    {cls:24s} {n}")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("  Anchor validation")
    print("═══════════════════════════════════════════════════════════════")
    v = validate()
    print(f"  modules anchored:  {v['modules']}")
    print(f"  total anchors:     {v['anchors_total']}")
    print(f"  Ω in register:     {v['omega_in_register']}")
    print(f"  valid:             {v['valid']}")
    if not v["valid"]:
        print(f"  invalid:           {json.dumps(v['invalid'], indent=2)}")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("  Chains (every module → Ω)")
    print("═══════════════════════════════════════════════════════════════")
    for chain in terminate_all():
        print(render(chain))
        print()

    # terminal summary
    print("═══════════════════════════════════════════════════════════════")
    print("  Terminal of everything")
    print("═══════════════════════════════════════════════════════════════")
    print(f"  {R.get('Ω').id}  {R.get('Ω').name}")
    print(f"  source: {R.get('Ω').source}")
    print(f"  arity:  {R.get('Ω').arity}")
    print()
    print("  Every module above terminates here. The register")
    print("  declares its own residual (T-38 / C-B4). Our anchor")
    print("  map inherits the same: it is complete up to the")
    print("  modules listed. Adding a module is the act of")
    print("  proceeding — Ω.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
