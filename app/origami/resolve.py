"""Name resolution — replace undefined names in function bodies
with the nearest parameter.

This is a heuristic. It runs after assembly, before verification.
For each function:
  - find names used but not defined (params, builtins, imports)
  - if exactly one undefined name and at least one parameter,
    rewrite the undefined name to the first parameter
"""
from __future__ import annotations

import ast
import builtins

_BUILTINS = set(dir(builtins)) | {
    "True", "False", "None", "self", "cls",
    "__name__", "__file__", "__doc__", "__builtins__",
    "__package__", "annotations",
}


def _param_names(fn: ast.AST) -> list[str]:
    out = []
    for a in getattr(fn.args, "args", []):
        out.append(a.arg)
    for a in getattr(fn.args, "posonlyargs", []):
        out.append(a.arg)
    for a in getattr(fn.args, "kwonlyargs", []):
        out.append(a.arg)
    if fn.args.vararg:
        out.append(fn.args.vararg.arg)
    if fn.args.kwarg:
        out.append(fn.args.kwarg.arg)
    return out


def _defined_names(tree: ast.AST) -> set[str]:
    out = set(_BUILTINS)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                out.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                out.add(a.asname or a.name)
        elif isinstance(n, ast.arg):
            out.add(n.arg)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out.add(t.id)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) or isinstance(n, ast.For) and isinstance(n.target, ast.Name):
            out.add(n.target.id)
        elif isinstance(n, ast.withitem) and isinstance(n.optional_vars, ast.Name):
            out.add(n.optional_vars.id)
        elif isinstance(n, ast.comprehension) and isinstance(n.target, ast.Name):
            out.add(n.target.id)
    return out


def _undefined_in_function(fn: ast.AST, top_defined: set[str]) -> list[str]:
    params = set(_param_names(fn))
    local = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    local.add(t.id)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) or isinstance(n, ast.For) and isinstance(n.target, ast.Name):
            local.add(n.target.id)
        elif isinstance(n, ast.withitem) and isinstance(n.optional_vars, ast.Name):
            local.add(n.optional_vars.id)
        elif isinstance(n, ast.comprehension) and isinstance(n.target, ast.Name):
            local.add(n.target.id)
    used = {x.id for x in ast.walk(fn)
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)}
    return sorted(used - params - local - top_defined)


def resolve(source: str) -> str:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source
    top_defined = _defined_names(tree)
    lines = source.splitlines()

    # gather edits: (line_index, old, new)
    edits = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name.startswith("test_"):
            continue
        params = _param_names(fn)
        if not params:
            continue
        undef = _undefined_in_function(fn, top_defined)
        if len(undef) != 1:
            continue
        old = undef[0]
        new = params[0]
        if old == new:
            continue
        start = fn.lineno
        end = getattr(fn, "end_lineno", start)
        for i in range(start - 1, end):
            edits.append((i, old, new))

    for i, old, new in edits:
        line = lines[i]
        # word-boundary replacement
        out = []
        j = 0
        while j < len(line):
            if line.startswith(old, j):
                before = line[j - 1] if j > 0 else ""
                after_pos = j + len(old)
                after = line[after_pos] if after_pos < len(line) else ""
                if not (before.isalnum() or before == "_") and \
                   not (after.isalnum() or after == "_"):
                    out.append(new)
                    j += len(old)
                    continue
            out.append(line[j])
            j += 1
        lines[i] = "".join(out)

    return "\n".join(lines)


def resolve_tests(source: str) -> str:
    """For each test body, if it calls an undefined function name,
    try the nearest function with a matching suffix."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source

    funcs = [n.name for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
             and not n.name.startswith("test_")]
    if not funcs:
        return source

    tests = [n for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
             and n.name.startswith("test_")]
    lines = source.splitlines()
    edits = []
    for t in tests:
        local_defs = _defined_names(t)
        used = {x.id for x in ast.walk(t)
                if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)}
        unknown = used - local_defs - set(_param_names(t))
        for name in unknown:
            # pick the function whose name contains the unknown token
            cands = [f for f in funcs
                     if name in f or f.startswith(name)
                     or name.replace("_", "") in f.replace("_", "")]
            if not cands:
                # fall back to first function
                cands = funcs
            new = cands[0]
            start = t.lineno
            end = getattr(t, "end_lineno", start)
            for i in range(start - 1, end):
                edits.append((i, name, new))

    for i, old, new in edits:
        line = lines[i]
        out = []
        j = 0
        while j < len(line):
            if line.startswith(old, j):
                before = line[j - 1] if j > 0 else ""
                after_pos = j + len(old)
                after = line[after_pos] if after_pos < len(line) else ""
                if not (before.isalnum() or before == "_") and \
                   not (after.isalnum() or after == "_"):
                    out.append(new)
                    j += len(old)
                    continue
            out.append(line[j])
            j += 1
        lines[i] = "".join(out)

    return "\n".join(lines)
