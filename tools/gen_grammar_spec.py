#!/usr/bin/env python3
"""Generative grammar spec docs for any Python codebase.

Walks a directory, extracts every module's public interface, then emits:
  - <out>/grammar.ebnf     formal EBNF of the codebase's symbol graph
  - <out>/SPEC.md          human-readable grammar spec
  - <out>/index.json       machine-readable symbol index
  - <out>/imports.dot      Graphviz import graph

Usage:
  python3 tools/gen_grammar_spec.py <root-dir> [<out-dir>]
"""
from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Symbol:
    kind: str                    # "class" | "function" | "method" | "constant" | "typealias"
    name: str
    qualname: str                # dotted, includes class prefix for methods
    module: str                  # dotted module path
    lineno: int
    docstring: str = ""
    decorators: list[str] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    returns: str = ""
    raises: list[str] = field(default_factory=list)
    is_async: bool = False
    is_private: bool = False


@dataclass
class Module:
    name: str                    # dotted
    path: str                    # relative posix path
    docstring: str = ""
    imports: list[str] = field(default_factory=list)
    from_imports: list[tuple[str, str]] = field(default_factory=list)
    symbols: list[Symbol] = field(default_factory=list)
    __all__: list[str] = field(default_factory=list)
    is_package: bool = False


@dataclass
class Codebase:
    root: str
    modules: list[Module] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Walk
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", ".lanes", "node_modules", ".next",
    "__pycache__", ".mypy_cache", ".ruff_cache", ".hypothesis",
    ".pytest_cache", ".eggs", "build", "dist", ".tox", ".cache",
    ".codeql-results", ".mesh-codeql-db", ".snapshots", ".delta",
    ".last-backups", ".complete-backups", ".benchmarks", ".agency",
    ".backrooms", ".moat", ".murmur", "site-packages",
}


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
        if part.endswith(".egg-info"):
            return True
    return False


def module_name(root: Path, py: Path) -> str:
    rel = py.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else "__root__"


# ---------------------------------------------------------------------------
# AST extraction
# ---------------------------------------------------------------------------

def _unparse(node) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _decorator_names(node) -> list[str]:
    out = []
    for dec in getattr(node, "decorator_list", []) or []:
        out.append(_unparse(dec))
    return out


def _arg_names(args: ast.arguments) -> list[str]:
    out = []
    posonly = getattr(args, "posonlyargs", []) or []
    for a in list(posonly) + list(args.args):
        out.append(a.arg)
    if args.vararg:
        out.append("*" + args.vararg.arg)
    for a in args.kwonlyargs:
        out.append(a.arg)
    if args.kwarg:
        out.append("**" + args.kwarg.arg)
    return out


def _raises(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    out = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Raise) and node.exc is not None:
            out.append(_unparse(node.exc))
    return out


def extract_module(py: Path, root: Path) -> Module:
    src = py.read_text(errors="replace")
    tree = ast.parse(src, filename=str(py))
    mod = Module(
        name=module_name(root, py),
        path=str(py.relative_to(root).as_posix()),
        docstring=ast.get_docstring(tree) or "",
        is_package=py.name == "__init__.py",
    )

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                base = "." * node.level + base
            for alias in node.names:
                mod.from_imports.append((base, alias.name))
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    try:
                        value = ast.literal_eval(node.value)
                        if isinstance(value, list):
                            mod.__all__ = [str(x) for x in value]
                    except Exception:
                        pass
                elif isinstance(t, ast.Name) and t.id.isupper():
                    mod.symbols.append(Symbol(
                        kind="constant",
                        name=t.id,
                        qualname=t.id,
                        module=mod.name,
                        lineno=node.lineno,
                    ))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id.isupper():
                mod.symbols.append(Symbol(
                    kind="constant",
                    name=node.target.id,
                    qualname=node.target.id,
                    module=mod.name,
                    lineno=node.lineno,
                ))
        elif isinstance(node, ast.ClassDef):
            mod.symbols.append(Symbol(
                kind="class",
                name=node.name,
                qualname=node.name,
                module=mod.name,
                lineno=node.lineno,
                docstring=ast.get_docstring(node) or "",
                decorators=_decorator_names(node),
                bases=[_unparse(b) for b in node.bases],
                is_private=node.name.startswith("_"),
            ))
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    mod.symbols.append(Symbol(
                        kind="method",
                        name=sub.name,
                        qualname=f"{node.name}.{sub.name}",
                        module=mod.name,
                        lineno=sub.lineno,
                        docstring=ast.get_docstring(sub) or "",
                        decorators=_decorator_names(sub),
                        args=_arg_names(sub.args),
                        returns=_unparse(sub.returns) if sub.returns else "",
                        raises=_raises(sub),
                        is_async=isinstance(sub, ast.AsyncFunctionDef),
                        is_private=sub.name.startswith("_"),
                    ))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            mod.symbols.append(Symbol(
                kind="function",
                name=node.name,
                qualname=node.name,
                module=mod.name,
                lineno=node.lineno,
                docstring=ast.get_docstring(node) or "",
                decorators=_decorator_names(node),
                args=_arg_names(node.args),
                returns=_unparse(node.returns) if node.returns else "",
                raises=_raises(node),
                is_async=isinstance(node, ast.AsyncFunctionDef),
                is_private=node.name.startswith("_"),
            ))

    return mod


def walk_codebase(root: Path) -> Codebase:
    cb = Codebase(root=str(root))
    for py in sorted(root.rglob("*.py")):
        if should_skip(py.relative_to(root)):
            continue
        try:
            cb.modules.append(extract_module(py, root))
        except SyntaxError as e:
            cb.errors.append((str(py.relative_to(root)), f"SyntaxError: {e}"))
        except Exception as e:
            cb.errors.append((str(py.relative_to(root)), f"{type(e).__name__}: {e}"))
    return cb


# ---------------------------------------------------------------------------
# Emit EBNF
# ---------------------------------------------------------------------------

def _sanitize_rule(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not s or not s[0].isalpha():
        s = "R_" + s
    return s


def _module_rule(mod: Module) -> str:
    return _sanitize_rule(mod.name)


def emit_ebnf(cb: Codebase) -> str:
    lines = []
    lines.append("(* ===============================================================")
    lines.append(f"   Codebase grammar for: {cb.root}")
    lines.append(f"   Modules: {len(cb.modules)}")
    lines.append(f"   Symbols: {sum(len(m.symbols) for m in cb.modules)}")
    lines.append("   =============================================================== *)")
    lines.append("")
    lines.append("Codebase        = { Module } ;")
    lines.append("")

    for mod in cb.modules:
        rule = _module_rule(mod)
        lines.append(f"(* {mod.path} *)")
        parts = []
        for s in mod.symbols:
            if s.is_private and s.kind not in ("class",):
                continue
            sym_rule = f"{rule}.{_sanitize_rule(s.qualname)}"
            parts.append(sym_rule)
        if not parts:
            lines.append(f"{rule}            = <empty> ;")
        elif len(parts) == 1:
            lines.append(f"{rule}            = {parts[0]} ;")
        else:
            first = f"{rule}            = {parts[0]}"
            lines.append(first)
            for p in parts[1:-1]:
                lines.append(f"                | {p}")
            lines.append(f"                | {parts[-1]} ;")
        lines.append("")

    # Symbol definitions
    lines.append("(* ---- Symbol definitions ---- *)")
    lines.append("")
    for mod in cb.modules:
        rule = _module_rule(mod)
        for s in mod.symbols:
            if s.is_private and s.kind not in ("class",):
                continue
            sym_rule = f"{rule}.{_sanitize_rule(s.qualname)}"
            if s.kind == "class":
                bases = " , ".join(_sanitize_rule(b) for b in s.bases) if s.bases else "object"
                methods = [_sanitize_rule(m.name) for m in mod.symbols
                           if m.kind == "method" and m.qualname.startswith(s.name + ".")]
                body = " , ".join([f"BASE({bases})"] + [f"METHOD({m})" for m in methods])
                lines.append(f"{sym_rule} = {body} ;")
            elif s.kind == "method":
                args = " , ".join(_sanitize_rule(a) for a in s.args) if s.args else "self"
                ret = _sanitize_rule(s.returns) if s.returns else "Any"
                lines.append(f"{sym_rule} = ARGS( {args} ) , RETURNS( {ret} ) ;")
            elif s.kind == "function":
                args = " , ".join(_sanitize_rule(a) for a in s.args) if s.args else "void"
                ret = _sanitize_rule(s.returns) if s.returns else "Any"
                lines.append(f"{sym_rule} = ARGS( {args} ) , RETURNS( {ret} ) ;")
            elif s.kind == "constant":
                lines.append(f"{sym_rule} = CONSTANT ;")
        lines.append("")

    # Import edges
    lines.append("(* ---- Imports ---- *)")
    lines.append("")
    edges = []
    for mod in cb.modules:
        src = _module_rule(mod)
        for name in mod.imports:
            edges.append((src, _sanitize_rule(name)))
        for base, sym in mod.from_imports:
            edges.append((src, _sanitize_rule(base)))
    seen = set()
    for src, dst in edges:
        key = (src, dst)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"{src} -> {dst} ;")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Emit SPEC.md
# ---------------------------------------------------------------------------

def emit_spec(cb: Codebase) -> str:
    lines = []
    lines.append(f"# Grammar Specification: `{cb.root}`")
    lines.append("")
    lines.append(f"- Modules: **{len(cb.modules)}**")
    total_syms = sum(len(m.symbols) for m in cb.modules)
    lines.append(f"- Symbols: **{total_syms}**")
    classes = sum(1 for m in cb.modules for s in m.symbols if s.kind == "class")
    funcs = sum(1 for m in cb.modules for s in m.symbols if s.kind == "function")
    methods = sum(1 for m in cb.modules for s in m.symbols if s.kind == "method")
    consts = sum(1 for m in cb.modules for s in m.symbols if s.kind == "constant")
    lines.append(f"- Classes: **{classes}**")
    lines.append(f"- Functions: **{funcs}**")
    lines.append(f"- Methods: **{methods}**")
    lines.append(f"- Constants: **{consts}**")
    if cb.errors:
        lines.append(f"- Parse errors: **{len(cb.errors)}**")
    lines.append("")
    lines.append("## Module index")
    lines.append("")
    lines.append("| Module | Path | Classes | Functions | Methods | Constants |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for mod in cb.modules:
        c = sum(1 for s in mod.symbols if s.kind == "class")
        f = sum(1 for s in mod.symbols if s.kind == "function")
        m = sum(1 for s in mod.symbols if s.kind == "method")
        k = sum(1 for s in mod.symbols if s.kind == "constant")
        lines.append(f"| `{mod.name}` | `{mod.path}` | {c} | {f} | {m} | {k} |")
    lines.append("")

    if cb.errors:
        lines.append("## Parse errors")
        lines.append("")
        for path, err in cb.errors:
            lines.append(f"- `{path}` — {err}")
        lines.append("")

    lines.append("## Module specifications")
    lines.append("")
    for mod in cb.modules:
        lines.append(f"### `{mod.name}`")
        lines.append("")
        lines.append(f"Path: `{mod.path}`")
        if mod.is_package:
            lines.append("Kind: package (`__init__.py`)")
        if mod.docstring:
            lines.append("")
            lines.append("> " + mod.docstring.strip().split("\n")[0])
        if mod.__all__:
            lines.append("")
            lines.append("**`__all__`**")
            lines.append("")
            for name in mod.__all__:
                lines.append(f"- `{name}`")
        lines.append("")
        classes = [s for s in mod.symbols if s.kind == "class"]
        funcs = [s for s in mod.symbols if s.kind == "function"]
        consts = [s for s in mod.symbols if s.kind == "constant"]
        if classes:
            lines.append("**Classes**")
            lines.append("")
            for c in classes:
                bases = ", ".join(c.bases) if c.bases else "object"
                lines.append(f"- `{c.name}` (L{c.lineno}) — bases: `{bases}`")
                methods = [s for s in mod.symbols
                           if s.kind == "method" and s.qualname.startswith(c.name + ".")]
                for m in methods:
                    args = ", ".join(m.args)
                    ret = f" -> {m.returns}" if m.returns else ""
                    mod_flag = "async " if m.is_async else ""
                    lines.append(f"    - `{mod_flag}{m.name}({args}){ret}` (L{m.lineno})")
                    if m.raises:
                        for r in sorted(set(m.raises)):
                            lines.append(f"        - raises: `{r}`")
            lines.append("")
        if funcs:
            lines.append("**Functions**")
            lines.append("")
            for f in funcs:
                args = ", ".join(f.args)
                ret = f" -> {f.returns}" if f.returns else ""
                mod_flag = "async " if f.is_async else ""
                lines.append(f"- `{mod_flag}{f.name}({args}){ret}` (L{f.lineno})")
                for dec in f.decorators:
                    lines.append(f"    - decorator: `{dec}`")
                for r in sorted(set(f.raises)):
                    lines.append(f"    - raises: `{r}`")
            lines.append("")
        if consts:
            lines.append("**Constants**")
            lines.append("")
            for k in consts:
                lines.append(f"- `{k.name}` (L{k.lineno})")
            lines.append("")
        if mod.imports or mod.from_imports:
            lines.append("**Imports**")
            lines.append("")
            for name in sorted(set(mod.imports)):
                lines.append(f"- `import {name}`")
            for base, sym in sorted(set(mod.from_imports)):
                lines.append(f"- `from {base} import {sym}`")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Emit index + dot
# ---------------------------------------------------------------------------

def emit_index(cb: Codebase) -> str:
    data = {
        "root": cb.root,
        "module_count": len(cb.modules),
        "symbol_count": sum(len(m.symbols) for m in cb.modules),
        "error_count": len(cb.errors),
        "errors": cb.errors,
        "modules": [asdict(m) for m in cb.modules],
    }
    return json.dumps(data, indent=2)


def emit_dot(cb: Codebase) -> str:
    lines = ["digraph imports {", '  rankdir=LR;', '  node [shape=box, fontname="Helvetica"];']
    for mod in cb.modules:
        label = mod.name.replace('"', "'")
        lines.append(f'  "{label}";')
    seen = set()
    for mod in cb.modules:
        src = mod.name
        for base, _sym in mod.from_imports:
            if base.startswith("."):
                continue
            key = (src, base)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f'  "{src}" -> "{base}";')
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python3 tools/gen_grammar_spec.py <root-dir> [<out-dir>]")
        return 2

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2

    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else root / "_grammar_spec"
    out.mkdir(parents=True, exist_ok=True)

    print(f"scanning {root}")
    cb = walk_codebase(root)
    print(f"  modules: {len(cb.modules)}")
    print(f"  symbols: {sum(len(m.symbols) for m in cb.modules)}")
    print(f"  errors:  {len(cb.errors)}")

    (out / "grammar.ebnf").write_text(emit_ebnf(cb))
    (out / "SPEC.md").write_text(emit_spec(cb))
    (out / "index.json").write_text(emit_index(cb))
    (out / "imports.dot").write_text(emit_dot(cb))

    print(f"wrote {out}/grammar.ebnf")
    print(f"wrote {out}/SPEC.md")
    print(f"wrote {out}/index.json")
    print(f"wrote {out}/imports.dot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
