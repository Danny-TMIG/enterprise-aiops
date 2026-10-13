"""Prove the sheaf site works on real runs.

For each prompt:
    - dispatch with the rich_module grammar
    - record: does the site resolve every leaf to an open?
    - record: does cocycle_check pass?
    - record: does gluing produce parseable code?
    - record: does the code reference names it does not define?
"""
from __future__ import annotations

import ast
import builtins
import sys

from app.origami.dispatch import dispatch
from app.origami.library import get as get_grammar
from app.origami.sheaf import site_summary
from app.origami.swarm import Swarm

PROMPTS = [
    "add rate limiting to /api/checkout",
    "add a health check to /status",
    "compute a checksum of a string",
    "parse an environment variable as an integer",
    "return the smaller of two integers",
    "count the words in a string",
    "reverse a list",
    "return the length of a string",
    "check if a number is prime",
    "sum a list of integers",
]

_B = set(dir(builtins)) | {
    "__name__", "__file__", "__doc__", "__builtins__", "__package__",
}


def _undef(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["<syntax>"]
    defd = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defd.add(node.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                defd.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                defd.add(a.asname or a.name)
        elif isinstance(node, ast.arg):
            defd.add(node.arg)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    defd.add(t.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) or isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            defd.add(node.target.id)
        elif isinstance(node, ast.withitem) and isinstance(node.optional_vars, ast.Name):
            defd.add(node.optional_vars.id)
        elif isinstance(node, ast.comprehension):
            t = node.target
            if isinstance(t, ast.Name):
                defd.add(t.id)
    used = {n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    return sorted(used - defd - _B)


def main() -> int:
    print("-- sheaf proof: 10 prompts --")
    print(f"site: {site_summary()['opens']}")
    print()
    swarm = Swarm(n_workers=1)
    grammar = get_grammar("rich_module")

    cols = ["glued", "parses", "cocyc_ok", "no_undef"]
    totals = {c: 0 for c in cols}
    rows = []
    for i, prompt in enumerate(PROMPTS):
        r = dispatch(grammar, swarm, intent=prompt,
                     seed=i, max_depth=10, max_tokens=128)
        glued = bool(r.code)
        parses = False
        und: list[str] = []
        if glued:
            try:
                ast.parse(r.code)
                parses = True
            except SyntaxError:
                parses = False
            if parses:
                und = _undef(r.code)
        flags = {
            "glued": glued,
            "parses": parses,
            "cocyc_ok": bool(r.cocycle_ok),
            "no_undef": parses and not und,
        }
        for c in cols:
            totals[c] += int(flags[c])
        rows.append((prompt, flags, r, und))

    for prompt, flags, r, und in rows:
        mark = "".join("1" if flags[c] else "0" for c in cols)
        note = ""
        if r.violations:
            note = " cyc=" + str(r.violations[:1])
        elif und and und[0] != "<syntax>":
            note = " und=" + str(und[:2])
        print(f"  [{mark}] {prompt[:40]:40s}{note}")
    print()
    print(f"  {'glued':10s} {totals['glued']}/{len(PROMPTS)}")
    print(f"  {'parses':10s} {totals['parses']}/{len(PROMPTS)}")
    print(f"  {'cocyc_ok':10s} {totals['cocyc_ok']}/{len(PROMPTS)}")
    print(f"  {'no_undef':10s} {totals['no_undef']}/{len(PROMPTS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
