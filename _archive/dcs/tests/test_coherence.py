"""Unit tests for dcs.coherence."""

from dcs.coherence import coherent, incoherent_keys


def test_scalar_values_cohere_with_themselves():
    assert coherent(1, 1)
    assert coherent("x", "x")
    assert coherent(None, None)


def test_scalars_do_not_cohere_across_types():
    assert not coherent(1, "1")


def test_dicts_cohere_regardless_of_key_order():
    assert coherent({"a": 1, "b": 2}, {"b": 2, "a": 1})


def test_dicts_do_not_cohere_when_values_differ():
    assert not coherent({"a": 1}, {"a": 2})


def test_lists_cohere_when_equal():
    assert coherent([1, 2, 3], [1, 2, 3])
    assert not coherent([1, 2, 3], [3, 2, 1])


def test_incoherent_keys_reports_differences():
    a = {"x": 1, "y": 2, "z": 3}
    b = {"x": 1, "y": 9, "w": 4}
    assert incoherent_keys(a, b) == ["w", "y", "z"]


def test_incoherent_keys_empty_when_all_cohere():
    assert incoherent_keys({"a": 1}, {"a": 1}) == []
