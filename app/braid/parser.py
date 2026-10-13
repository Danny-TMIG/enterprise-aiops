"""Braid workflow language. Real parser, real compiler.

Syntax:
    workflow NAME {
        source IDENT = call("arg")
        source IDENT = call("arg")
        braid IDENT = ref + ref
        transform IDENT = ref |> name
        emit ref
    }
Compiles to a plan dict with tasks in topological order.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Workflow:
    name: str
    statements: list[dict]

_HEADER = re.compile(r'^workflow\s+(\w+)\s*\{\s*$')
_CLOSE = re.compile(r'^\}\s*$')
_SRC = re.compile(r'^source\s+(\w+)\s*=\s*(\w+)\("([^"]*)"\)\s*$')
_BRAID = re.compile(r'^braid\s+(\w+)\s*=\s*(\w+)\s*\+\s*(\w+)\s*$')
_TRF = re.compile(r'^transform\s+(\w+)\s*=\s*(\w+)\s*\|>\s*(\w+)\s*$')
_EMIT = re.compile(r'^emit\s+(\w+)\s*$')

def parse_workflow(src: str) -> Workflow:
    lines = [l.strip() for l in src.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
    if not lines: raise ValueError("empty workflow")
    m = _HEADER.match(lines[0])
    if not m: raise ValueError(f"expected workflow header, got {lines[0]!r}")
    name = m.group(1)
    if not _CLOSE.match(lines[-1]): raise ValueError("missing closing brace")
    stmts = []
    for line in lines[1:-1]:
        for rx, kind in [(_SRC, "source"),(_BRAID, "braid"),(_TRF, "transform"),(_EMIT, "emit")]:
            mm = rx.match(line)
            if mm: stmts.append({"kind": kind, "parts": mm.groups()}); break
        else:
            raise ValueError(f"cannot parse: {line!r}")
    return Workflow(name=name, statements=stmts)

def compile_workflow(wf: Workflow) -> dict:
    defined = set()
    tasks = []
    for st in wf.statements:
        k, p = st["kind"], st["parts"]
        if k == "source":
            tid, op, arg = p
            if tid in defined: raise ValueError(f"duplicate {tid}")
            tasks.append({"op":"fetch","target":tid,"fn":op,"args":[arg]}); defined.add(tid)
        elif k == "braid":
            tid, a, b = p
            if a not in defined or b not in defined: raise ValueError(f"undefined ref in braid {tid}")
            tasks.append({"op":"braid","target":tid,"inputs":[a,b]}); defined.add(tid)
        elif k == "transform":
            tid, a, fn = p
            if a not in defined: raise ValueError(f"undefined ref in transform {tid}")
            tasks.append({"op":"transform","target":tid,"inputs":[a],"fn":fn}); defined.add(tid)
        elif k == "emit":
            (a,) = p
            if a not in defined: raise ValueError(f"undefined emit {a}")
            tasks.append({"op":"emit","inputs":[a]})
    return {"name": wf.name, "tasks": tasks}
