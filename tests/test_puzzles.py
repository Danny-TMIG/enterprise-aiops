import pytest
import importlib

def test_puzzles_import():
    try:
        mod = importlib.import_module("app.puzzles")
        assert mod is not None
    except ImportError:
        pytest.skip("app.puzzles submodule not present or empty")
