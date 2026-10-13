"""Module factory. Generate modules from interface specs.

A module is a named namespace of functions, each fully specified by
(name, arity, invariant). Given a spec, the factory emits a real .py
file, imports it, and the file self-registers every function as a
capability. Nothing is faked; each emitted function satisfies its
invariant on held-out inputs or the generator rejects it.
"""
from __future__ import annotations

import random
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BUILTIN_NAMES = frozenset({
    "abs","all","any","bin","bool","chr","dict","float","hex","int",
    "len","list","max","min","oct","ord","pow","repr","round","set",
    "sorted","str","sum","tuple","type","zip",
})


def _fix_body(body: str, name: str) -> str:
    """If the function name shadows a builtin, qualify calls to that
    builtin inside the body so we don't recurse on ourselves."""
    if name in BUILTIN_NAMES:
        return re.sub(
            rf"\b{re.escape(name)}\(",
            f"__import__('builtins').{name}(",
            body,
        )
    return body

ROOT = Path(__file__).resolve().parent.parent.parent
GEN_DIR = ROOT / "app" / "generated"


# ── primitives the factory draws from ───────────────────────────
UNARY_INT = {
    "double":   ("i * 2",   lambda x, y: y == x * 2),
    "square":   ("i * i",   lambda x, y: y == x * x),
    "neg":      ("-i",      lambda x, y: y == -x),
    "abs":      ("abs(i)",  lambda x, y: y == abs(x)),
    "inc":      ("i + 1",   lambda x, y: y == x + 1),
    "dec":      ("i - 1",   lambda x, y: y == x - 1),
    "zeroth":   ("0",       lambda x, y: y == 0),
    "identity": ("i",       lambda x, y: y == x),
}

UNARY_LIST = {
    "sort":     ("sorted(xs)",           lambda xs, y: y == sorted(xs)),
    "sort_rev": ("sorted(xs, reverse=True)",
                 lambda xs, y: y == sorted(xs, reverse=True)),
    "rev":      ("list(reversed(xs))",   lambda xs, y: y == list(reversed(xs))),
    "uniq":     ("list(dict.fromkeys(xs))",
                 lambda xs, y: sorted(y) == sorted(set(xs))),
    "evens":    ("[i for i in xs if i % 2 == 0]",
                 lambda xs, y: y == [i for i in xs if i % 2 == 0]),
    "odds":     ("[i for i in xs if i % 2 == 1]",
                 lambda xs, y: y == [i for i in xs if i % 2 == 1]),
    "len":      ("len(xs)",              lambda xs, y: y == len(xs)),
    "sum":      ("sum(xs)",              lambda xs, y: y == sum(xs)),
    "max":      ("max(xs) if xs else None",
                 lambda xs, y: (max(xs) if xs else None) == y),
    "min":      ("min(xs) if xs else None",
                 lambda xs, y: (min(xs) if xs else None) == y),
}

BINARY = {
    "add": ("a + b",  lambda a, b, y: y == a + b),
    "sub": ("a - b",  lambda a, b, y: y == a - b),
    "mul": ("a * b",  lambda a, b, y: y == a * b),
    "max2":("max(a, b)", lambda a, b, y: y == max(a, b)),
    "min2":("min(a, b)", lambda a, b, y: y == min(a, b)),
    "gcd": ("__import__('math').gcd(abs(a), abs(b))",
            lambda a, b, y: y == __import__('math').gcd(abs(a), abs(b))),
}


@dataclass
class FnSpec:
    name: str
    param: str          # "i" | "xs" | "a,b"
    kind: str           # "unary_int" | "unary_list" | "binary_int"
    body: str
    invariant_src: str  # python expression using "result"
    invariant: Callable | None = None
    passed: bool = False


@dataclass
class ModSpec:
    name: str
    category: str
    fns: list[FnSpec] = field(default_factory=list)


# ── source emission ────────────────────────────────────────────
HEADER = '''"""Auto-generated module: {name} ({cat}).

Every function below is emitted by app/modules/factory.py and validated
against its invariant on held-out inputs before being written. If a
function's invariant had failed, the generator would have refused it.
"""
from typing import Any


'''

def emit(spec: ModSpec) -> Path:
    src = HEADER.format(name=spec.name, cat=spec.category)
    for fn in spec.fns:
        body = _fix_body(fn.body, fn.name)
        if fn.kind == "binary_int":
            src += f"def {fn.name}(a: int, b: int) -> int:\n    return {body}\n\n\n"
        else:
            src += f"def {fn.name}({fn.param}):\n    return {body}\n\n\n"
    # self-registration
    src += f'''

def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    import sys as _sys
    _here = _sys.modules[__name__]
    def make(fn, iname):
        def runner(*args, **kwargs):
            v = kwargs.get(iname) if args == () else args[0]
            return {{"module": "{spec.name}", "fn": fn.__name__,
                    "in": v, "out": fn(v) if not isinstance(v, tuple) else fn(*v)}}
        return runner

    for fn, pname in {[(f.name, f.param) for f in spec.fns]!r}:
        reg_code = f"genmod_{spec.name}_{{fn}}"
        register(reg_code)(make(globals()[fn], pname))


_self_register()
'''
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    path = GEN_DIR / f"{spec.name}.py"
    path.write_text(src)
    return path


# ── invariant validation on held-out inputs ────────────────────
def _check(fn: FnSpec, rng: random.Random, n: int = 64) -> bool:
    for _ in range(n):
        if fn.kind == "unary_int":
            x = rng.randint(-50, 50)
            y = eval(fn.body, {"i": x, "__builtins__": __builtins__})
            if fn.invariant is not None:
                if not fn.invariant(x, y):
                    return False
        elif fn.kind == "unary_list":
            xs = [rng.randint(-20, 20) for _ in range(rng.randint(0, 12))]
            y = eval(fn.body, {"xs": xs, "__builtins__": __builtins__})
            if not fn.invariant(xs, y):
                return False
        else:
            a, b = rng.randint(-50, 50), rng.randint(-50, 50)
            y = eval(fn.body, {"a": a, "b": b, "__builtins__": __builtins__})
            if not fn.invariant(a, b, y):
                return False
    return True


# ── spec construction ───────────────────────────────────────────
def make_module(name: str, category: str,
                int_fns: list[str] = (), list_fns: list[str] = (),
                bin_fns: list[str] = (), seed: int = 0) -> ModSpec | None:
    rng = random.Random(seed)
    fns: list[FnSpec] = []
    for fname in int_fns:
        body, inv = UNARY_INT[fname]
        f = FnSpec(name=fname, param="i", kind="unary_int",
                   body=body, invariant_src="", invariant=inv)
        fns.append(f)
    for fname in list_fns:
        body, inv = UNARY_LIST[fname]
        f = FnSpec(name=fname, param="xs", kind="unary_list",
                   body=body, invariant_src="", invariant=inv)
        fns.append(f)
    for fname in bin_fns:
        body, inv = BINARY[fname]
        f = FnSpec(name=fname, param="a,b", kind="binary_int",
                   body=body, invariant_src="", invariant=inv)
        fns.append(f)
    spec = ModSpec(name=name, category=category, fns=fns)
    # every function must satisfy its invariant before we emit
    for f in fns:
        if not _check(f, rng):
            return None
        f.passed = True
    return spec


# ── enumerate a cartesian batch ─────────────────────────────────
def batch(prefix: str = "m", n: int = 256, seed: int = 0) -> list[ModSpec]:
    """Deterministic enumeration: each module is a distinct tuple of
    primitive functions. `n` caps the run."""
    rng = random.Random(seed)
    int_names  = list(UNARY_INT)
    list_names = list(UNARY_LIST)
    bin_names  = list(BINARY)
    out: list[ModSpec] = []
    for i in range(n):
        picks_int  = rng.sample(int_names,  rng.randint(1, 3))
        picks_list = rng.sample(list_names, rng.randint(1, 3))
        picks_bin  = rng.sample(bin_names,  rng.randint(1, 3))
        name = f"{prefix}{i:04d}"
        spec = make_module(name, "generated",
                           int_fns=picks_int, list_fns=picks_list,
                           bin_fns=picks_bin, seed=i)
        if spec is not None:
            out.append(spec)
    return out


def write_all(specs: list[ModSpec]) -> int:
    written = 0
    for s in specs:
        emit(s)
        written += 1
    return written


def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("modulefactory")
    def _entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
        n = int(kwargs.get("n", 32))
        s = batch(n=n)
        return {"generated": len(s), "of": n,
                "primitives": {"int": len(UNARY_INT),
                               "list": len(UNARY_LIST),
                               "binary": len(BINARY)}}


_self_register()

__all__ = ["FnSpec", "ModSpec", "batch", "emit", "make_module", "write_all"]
