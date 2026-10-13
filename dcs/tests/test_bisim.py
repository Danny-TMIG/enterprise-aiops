"""Unit tests for dcs.bisim."""
from dcs.bisim import bisimilar, equivalence_classes


def test_identical_states_are_bisimilar():
    lts = {"a": [("tick", "a")]}
    assert bisimilar(lts, "a", "a")


def test_single_step_identical_states():
    lts = {"a": [("x", "c")], "b": [("x", "c")], "c": []}
    assert bisimilar(lts, "a", "b")


def test_states_differing_in_label_are_not_bisimilar():
    lts = {"a": [("x", "c")], "b": [("y", "c")], "c": []}
    assert not bisimilar(lts, "a", "b")


def test_states_differing_in_successor_are_not_bisimilar():
    lts = {"a": [("x", "c")], "b": [("x", "d")], "c": [], "d": [("z", "c")]}
    assert not bisimilar(lts, "a", "b")


def test_unknown_state_returns_false():
    assert not bisimilar({"a": []}, "a", "z")


def test_equivalence_classes_groups_bisimilar_states():
    lts = {"a": [("x", "c")], "b": [("x", "c")], "c": []}
    classes = equivalence_classes(lts)
    assert classes["a"] == classes["b"]
    assert classes["a"] != classes["c"]


def test_terminal_states_cohere():
    assert bisimilar({"a": [], "b": []}, "a", "b")


def test_same_shaped_cycles_are_bisimilar():
    lts = {"a": [("x", "a")], "b": [("x", "b")]}
    assert bisimilar(lts, "a", "b")
