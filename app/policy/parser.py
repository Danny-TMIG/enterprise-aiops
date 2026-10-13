"""Small policy DSL. Real AST validator, real eval.

Syntax:
    rule "name" when EXPR then ACTION ["message"]
    rule "name" when EXPR then ACTION ["message"]
ACTION in {allow, deny, log, escalate}
EXPR is a Python expression tree restricted to:
    identifiers, literals, comparisons, boolean ops, in, not, parens.
Attribute access, calls, comprehensions, lambdas, subscript are rejected.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Policy:
    name: str
    condition: str
    action: str
    message: str
    tree: ast.Expression

_RE = re.compile(r'^rule\s+"([^"]+)"\s+when\s+(.+?)\s+then\s+(\w+)(?:\s+"([^"]*)")?\s*$')

_BANNED = (ast.Attribute, ast.Call, ast.Lambda, ast.ListComp, ast.DictComp,
           ast.SetComp, ast.GeneratorExp, ast.Await, ast.Yield, ast.NamedExpr)
_ALLOWED_BINOPS = (ast.And, ast.Or)
_ALLOWED_CMPOPS = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Is, ast.IsNot)
_ALLOWED_UNARY = (ast.Not, ast.USub, ast.UAdd)

def _check_node(n):
    if isinstance(n, _BANNED): raise ValueError(f"banned node: {type(n).__name__}")
    for child in ast.walk(n):
        if isinstance(child, _BANNED): raise ValueError(f"banned: {type(child).__name__}")
        if isinstance(child, ast.BoolOp) and not isinstance(child.op, _ALLOWED_BINOPS):
            raise ValueError("banned boolop")
        if isinstance(child, ast.Compare):
            for op in child.ops:
                if not isinstance(op, _ALLOWED_CMPOPS):
                    raise ValueError(f"banned cmpop: {type(op).__name__}")
        if isinstance(child, ast.UnaryOp) and not isinstance(child.op, _ALLOWED_UNARY):
            raise ValueError(f"banned unary: {type(child.op).__name__}")

def parse_policy(src: str) -> list[Policy]:
    out = []
    for line in src.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        m = _RE.match(line)
        if not m: raise ValueError(f"cannot parse: {line!r}")
        name, cond, action, msg = m.groups()
        if action not in ("allow","deny","log","escalate"):
            raise ValueError(f"unknown action: {action}")
        tree = ast.parse(cond, mode="eval")
        _check_node(tree.body)
        out.append(Policy(name=name, condition=cond, action=action,
                          message=msg or "", tree=tree))
    return out

def evaluate(policies: list[Policy], ctx: dict[str, Any]) -> dict[str, Any]:
    """Return the first matching rule's action. If none match: default deny."""
    for p in policies:
        code = compile(p.tree, "<policy>", "eval")
        try:
            ok = bool(eval(code, {"__builtins__": {}}, ctx))
        except Exception:
            ok = False
        if ok:
            return {"rule": p.name, "action": p.action, "message": p.message, "matched": True}
    return {"rule": None, "action": "deny", "message": "no rule matched", "matched": False}
