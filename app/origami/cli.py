"""origami CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.origami.dispatch import dispatch
from app.origami.grammar import expand
from app.origami.library import get as get_grammar
from app.origami.library import list_shipped


def _cmd_expand(a) -> int:
    g = get_grammar(a.grammar)
    d = expand(g, max_depth=a.max_depth, seed=a.seed)
    if a.tree:
        print(json.dumps(d["tree"], indent=2, default=str))
        return 0
    print(json.dumps({
        "grammar": g.name, "seed": a.seed,
        "leaves": len(d["leaves"]),
        "terminals": d["terminals"],
    }, indent=2))
    return 0


def _cmd_swarm(a) -> int:
    from app.origami.swarm import Swarm
    g = get_grammar(a.grammar)
    s = Swarm(n_workers=a.workers)
    if not s.available():
        print("  ! MLX not available - running without swarm", file=sys.stderr)
    r = dispatch(g, s, seed=a.seed, max_depth=a.max_depth,
                 max_tokens=a.max_tokens)
    if getattr(a, 'refine', False):
        from app.origami.dispatch import refine as _refine
        r.code = _refine(r.code, s, max_tokens=a.max_tokens * 4)
    payload = {
        "grammar": r.grammar_name, "seed": r.seed,
        "leaves": r.leaves, "filled": r.filled,
        "swarm": r.swarm,
    }
    if a.out:
        Path(a.out).write_text(r.code or r.text)
        print(f"  wrote {a.out} ({len(r.text)} chars)")
    print(json.dumps(payload, indent=2, default=str))
    if a.print_text:
        print("-- text --")
        print(r.text)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="origami")
    p.add_argument("--grammar", default="code_artifact",
                   choices=list_shipped())
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-depth", type=int, default=10)
    p.add_argument("--max-tokens", type=int, default=128)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--swarm", action="store_true")
    p.add_argument("--out", default="")
    p.add_argument("--tree", action="store_true")
    p.add_argument("--print-text", action="store_true")
    p.add_argument("--refine", action="store_true",
                   help="run one refinement pass over the assembled code")
    a = p.parse_args(argv)
    if a.swarm or a.out:
        return _cmd_swarm(a)
    return _cmd_expand(a)


if __name__ == "__main__":
    sys.exit(main())
