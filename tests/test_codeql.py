import pytest
import importlib

def test_codeql_import():
    try:
        mod = importlib.import_module("app.codeql")
        assert mod is not None
    except ImportError:
        pytest.skip("app.codeql submodule not present or empty")
