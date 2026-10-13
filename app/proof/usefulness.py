"""Measure whether artifacts are useful.

Operational definition. An artifact is useful if it passes six:
  1. parses
  2. intent_match — a generated function name shares a keyword
  3. body_nonstub — at least one function has a real body
  4. test_present — at least one test_ function
  5. no_undefined — no undefined names
  6. no_placeholders — no template markers
"""
from __future__ import annotations

import ast
import builtins
import re
import sys

_B = set(dir(builtins)) | {
    "__name__", "__file__", "__doc__", "__builtins__", "__package__",
}
STOP = {"the", "a", "an", "to", "for", "of", "in", "on", "and", "or",
        "is", "are", "be", "with", "this", "that", "add", "create",
        "make", "implement", "return", "compute", "check", "if"}
PLACEHOLDERS = ("<FUNC", "<TEST", "<DOC", "small_function",
                "read_file", "value + 1", "TODO", "FIXME", "placeholder")


def _kw(text: str) -> set:
    """Split on spaces, underscores, hyphens, dots, slashes, and
    camelCase. Lowercase. Drop stopwords and short tokens."""
    spaced = re.sub(r"[_./\-]+", " ", text)
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", spaced)
    toks = re.findall(r"[A-Za-z][A-Za-z0-9]*", spaced.lower())
    return {t for t in toks if t not in STOP and len(t) >= 3}


def _func_names(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return [n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _undefined(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["<syntax>"]
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
        elif isinstance(node, ast.comprehension):
            t = node.target
            if isinstance(t, ast.Name):
                defined.add(t.id)
            elif isinstance(t, (ast.Tuple, ast.List)):
                for elt in t.elts:
                    if isinstance(elt, ast.Name):
                        defined.add(elt.id)
    used = {n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    return sorted(used - defined - _B)


def _body_nonstub(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name.startswith("test_"):
            continue
        for stmt in fn.body:
            if isinstance(stmt, ast.Pass):
                continue
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            return True
    return False


def _test_present(source: str) -> bool:
    return any(n.startswith("test_") for n in _func_names(source))


def _no_placeholders(source: str) -> bool:
    return not any(p in source for p in PLACEHOLDERS)


def score(intent: str, source: str) -> dict[str, object]:
    try:
        ast.parse(source)
        parses = True
    except SyntaxError:
        parses = False
    if not parses:
        return {"parses": False, "intent_match": False,
                "body_nonstub": False, "test_present": False,
                "no_undefined": False, "no_placeholders": False,
                "undefined_list": ["<syntax>"], "funcs": [],
                "useful": False, "score": 0.0}
    fn_tokens = set()
    for f in _func_names(source):
        fn_tokens |= _kw(f)
    im = bool(fn_tokens & _kw(intent))
    und = _undefined(source)
    body = _body_nonstub(source)
    test = _test_present(source)
    noph = _no_placeholders(source)
    checks = [parses, im, body, test, not und, noph]
    return {
        "parses": parses, "intent_match": im,
        "body_nonstub": body, "test_present": test,
        "no_undefined": not und, "no_placeholders": noph,
        "undefined_list": und, "funcs": _func_names(source),
        "useful": all(checks), "score": sum(int(c) for c in checks) / len(checks),
    }


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


def main() -> int:
    print("-- usefulness -- 10 prompts --")
    from app.origami.dispatch import dispatch
    from app.origami.library import get as get_grammar
    from app.origami.swarm import Swarm
    swarm = Swarm(n_workers=1)
    grammar = get_grammar("rich_module")
    tot = 0.0
    useful = 0
    for i, prompt in enumerate(PROMPTS):
        r = dispatch(grammar, swarm, intent=prompt,
                     seed=i, max_depth=6, max_tokens=128)
        s = score(prompt, r.code)
        tot += float(s["score"])
        useful += int(bool(s["useful"]))
        marks = "".join("1" if s[k] else "0" for k in
                        ("parses", "intent_match", "body_nonstub",
                         "test_present", "no_undefined", "no_placeholders"))
        print(f"  [{marks}] {prompt[:40]:40s} score={float(s['score']):.2f}")
    print(f"\n  useful: {useful}/{len(PROMPTS)}")
    print(f"  mean score: {tot/len(PROMPTS):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
