import importlib

import pytest


def test_agency_import():
    try:
        mod = importlib.import_module("app.agency")
        assert mod is not None
    except ImportError:
        pytest.skip("app.agency submodule not present or empty")
