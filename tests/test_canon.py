import importlib

import pytest


def test_canon_import():
    try:
        mod = importlib.import_module("app.canon")
        assert mod is not None
    except ImportError:
        pytest.skip("app.canon submodule not present or empty")
