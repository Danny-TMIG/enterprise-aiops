# SPDX-License-Identifier: MIT
"""Tests for app.origami.grammar."""
from app.origami.grammar import (
    LoadedGrammar,
    OrigamiGrammar,
    Production,
    Symbol,
    WeightedGrammar,
    expand,
)


def test_symbol():
    sym = Symbol(name="alpha")
    assert sym.name == "alpha"
    assert "alpha" in repr(sym)


def test_production():
    p = Production(left="S", right=["A", "B"])
    assert p.left == "S"
    assert p.right == ["A", "B"]
    assert "S" in repr(p)


def test_grammar_add_rule_accumulates():
    g = OrigamiGrammar()
    g.add_rule("S", "A")
    g.add_rule("S", "B")
    assert g.rules["S"] == ["A", "B"]


def test_grammar_initial_rules():
    g = OrigamiGrammar(rules={"S": ["A"]})
    g.add_rule("S", "B")
    assert g.rules["S"] == ["A", "B"]


def test_loaded_grammar_defaults():
    lg = LoadedGrammar()
    assert lg.start_symbol == "S"
    assert lg.rules == {}
    assert "LoadedGrammar" in repr(lg)


def test_weighted_grammar():
    wg = WeightedGrammar()
    wg.add_rule("S", "A", weight=0.5)
    wg.add_rule("S", "B", weight=0.5)
    assert wg.rules["S"] == [("A", 0.5), ("B", 0.5)]


def test_expand_terminal_returns_itself():
    g = OrigamiGrammar()
    assert expand(g, "A") == "A"


def test_expand_single_rule():
    g = OrigamiGrammar()
    g.add_rule("S", "A B")
    assert expand(g, "S") == "A B"


def test_expand_nested():
    g = OrigamiGrammar()
    g.add_rule("S", "A B")
    g.add_rule("A", "x")
    g.add_rule("B", "y")
    assert expand(g, "S") == "x y"


def test_expand_respects_max_depth():
    g = OrigamiGrammar()
    g.add_rule("S", "S")
    # depth 0 returns the symbol unchanged
    assert expand(g, "S", max_depth=0) == "S"


def test_expand_unknown_symbol():
    g = OrigamiGrammar()
    assert expand(g, "Z") == "Z"
