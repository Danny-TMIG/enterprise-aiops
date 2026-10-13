"""Claim 1: 7B output is 7B output. Measure it, don't assert it."""
from __future__ import annotations

import ast
import builtins
import sys
from typing import Any

from app.origami.dispatch import dispatch
from app.origami.library import get as get_grammar
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
    "find the maximum of three integers",
    "convert celsius to fahrenheit",
    "split a string by comma",
    "join a list of strings with dashes",
    "truncate a string to n characters",
    "check if a string is a palindrome",
    "compute factorial of a small integer",
    "return the average of a list",
    "strip whitespace from a string",
    "count occurrences of a character",
]

_B = set(dir(builtins)) | {
    "__name__", "__file__", "__doc__", "__builtins__", "__package__",
}


def undefined_names(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["<syntax_error>"]
    defined = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                defined.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                defined.add(a.asname or a.name)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    defined.add(t.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) or isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            defined.add(node.target.id)
        elif isinstance(node, ast.withitem) and isinstance(node.optional_vars, ast.Name):
            defined.add(node.optional_vars.id)
    used = {n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    return sorted(used - defined - _B)


def unused_params(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["<syntax_error>"]
    out = []
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = {a.arg for a in fn.args.args}
            used = {n.id for n in ast.walk(fn)
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
            for a in args:
                if a not in used:
                    out.append(f"{fn.name}({a})")
    return out


def return_consistent(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        ann = fn.returns
        if ann is None:
            continue
        bare = valued = 0
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Return):
                if sub.value is None:
                    bare += 1
                else:
                    valued += 1
        if isinstance(ann, ast.Constant) and ann.value is None:
            if valued > 0:
                return False
        else:
            if valued == 0 and bare > 0:
                return False
    return True


def no_stub_body(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if fn.name.startswith("test_"):
                continue
            for stmt in fn.body:
                if isinstance(stmt, ast.Pass):
                    continue
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                    continue
                return True
    return False


def score(source: str) -> dict[str, Any]:
    try:
        ast.parse(source)
        parse_ok = True
    except SyntaxError:
        parse_ok = False
    return {
        "parse": parse_ok,
        "no_undefined": parse_ok and not undefined_names(source),
        "no_unused_params": parse_ok and not unused_params(source),
        "return_consistent": parse_ok and return_consistent(source),
        "no_stub_body": parse_ok and no_stub_body(source),
        "undefined_list": undefined_names(source) if parse_ok else ["<syntax>"],
        "unused_list": unused_params(source) if parse_ok else ["<syntax>"],
    }


def main() -> int:
    print("── claim 1: 7B output is 7B output — 20-prompt suite ──")
    swarm = Swarm(n_workers=1)
    grammar = get_grammar("code_artifact")
    totals = {k: 0 for k in ("parse", "no_undefined", "no_unused_params",
                             "return_consistent", "no_stub_body")}
    all_pass = 0
    rows = []
    for i, prompt in enumerate(PROMPTS):
        try:
            r = dispatch(grammar, swarm, seed=i, max_depth=6, max_tokens=48)
            s = score(r.code)
        except Exception as e:
            s = {k: False for k in totals}
            s["undefined_list"] = [type(e).__name__]
            s["unused_list"] = []
        rows.append((prompt, s))
        for k in totals:
            totals[k] += int(bool(s.get(k)))
        if all(s.get(k) for k in totals):
            all_pass += 1

    n = len(PROMPTS)
    print(f"  {'axis':22s} pass/total")
    for k in totals:
        print(f"  {k:22s} {totals[k]}/{n}")
    print(f"  {'all_five_axes':22s} {all_pass}/{n}")
    print()
    for prompt, s in rows:
        marks = "".join("1" if s[k] else "0" for k in
                        ("parse", "no_undefined", "no_unused_params",
                         "return_consistent", "no_stub_body"))
        note = ""
        if s["undefined_list"] and s["undefined_list"][0] != "<syntax>":
            note += f" und={s['undefined_list'][:2]}"
        if s["unused_list"] and s["unused_list"][0] != "<syntax>":
            note += f" unused={s['unused_list'][:2]}"
        print(f"  [{marks}] {prompt[:42]:42s}{note}")
    print()
    print(f"  verdict: {all_pass}/{n} fully clean — 7B ceiling measured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
