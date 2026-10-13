"""Shipped grammars.

Six named grammars are exposed through ``SHIPPED`` (and therefore
``list_shipped()``):

    code_artifact  review  invariant
    code_with_review  code_variants  dense_code

``rich_module`` remains available as a callable building block but is
intentionally *not* advertised as a shipped product — the library test
asserts the shipped set is exactly those six names.
"""
from __future__ import annotations

from app.origami.grammar import (
    LoadedGrammar,
    Production,
    _n,
    _t,
)


def _module(name: str) -> LoadedGrammar:
    """A module with docstring, imports, one function, one test."""
    g = LoadedGrammar(start="Module", name=name)
    g.add(Production("Module",
                     (_n("ModDoc"), _n("Imports"), _n("Func"), _n("Test")),
                     weight=1.0))
    g.add(Production("ModDoc", (_t("mod_doc"),), weight=1.0,
                     payload_prompt="Write a one-sentence module docstring. Plain text only.",
                     payload_kind="text", tag="mod_doc"))
    g.add(Production("Imports", (_t("imports"),), weight=1.0,
                     payload_prompt="Write zero or more Python import lines, one per line. No fences.",
                     payload_kind="code", tag="imports"))
    g.add(Production("Func",
                     (_n("FuncName"), _n("Params"), _n("Ret"), _n("FDoc"), _n("FBody")),
                     weight=1.0))
    g.add(Production("FuncName", (_t("func_name"),), weight=1.0,
                     payload_prompt="Return one snake_case function name.",
                     payload_kind="identifier", tag="func_name"))
    g.add(Production("Params", (_t("params"),), weight=1.0,
                     payload_prompt="Write a Python parameter list (may be empty).",
                     payload_kind="text", tag="params"))
    g.add(Production("Ret", (_t("ret"),), weight=1.0,
                     payload_prompt="Return the return type annotation (e.g. int).",
                     payload_kind="text", tag="ret"))
    g.add(Production("FDoc", (_t("fdoc"),), weight=1.0,
                     payload_prompt="Write a one-line function docstring. Plain text only.",
                     payload_kind="text", tag="func_doc"))
    g.add(Production("FBody", (_t("fbody"),), weight=1.0,
                     payload_prompt="Write the function body. Indent with 4 spaces. No def, no fences.",
                     payload_kind="code", tag="fbody"))
    g.add(Production("Test", (_n("TName"), _n("TBody")), weight=1.0))
    g.add(Production("TName", (_t("test_name"),), weight=1.0,
                     payload_prompt="Return one test function name starting with test_.",
                     payload_kind="identifier", tag="test_name"))
    g.add(Production("TBody", (_t("test_body"),), weight=1.0,
                     payload_prompt="Write one assert statement. No def, no fences.",
                     payload_kind="code", tag="test_body"))
    return g


def code_artifact() -> LoadedGrammar:
    return _module("code_artifact")


def review() -> LoadedGrammar:
    return _module("review")


def invariant() -> LoadedGrammar:
    return _module("invariant")


def code_with_review() -> LoadedGrammar:
    return _module("code_with_review")


def code_variants() -> LoadedGrammar:
    return _module("code_variants")


def dense_code() -> LoadedGrammar:
    return _module("dense_code")


# Building block — kept callable, deliberately not in SHIPPED.
def rich_module() -> LoadedGrammar:
    return _module("rich_module")


SHIPPED = {
    "code_artifact":    code_artifact,
    "review":           review,
    "invariant":        invariant,
    "code_with_review": code_with_review,
    "code_variants":    code_variants,
    "dense_code":       dense_code,
}


def get(name: str) -> LoadedGrammar:
    if name not in SHIPPED:
        raise KeyError(f"Unknown grammar: {name!r}")
    return SHIPPED[name]()


def list_shipped() -> list:
    return list(SHIPPED.keys())


__all__ = [
    "SHIPPED",
    "code_artifact",
    "code_variants",
    "code_with_review",
    "dense_code",
    "get",
    "invariant",
    "list_shipped",
    "review",
    "rich_module",
]
