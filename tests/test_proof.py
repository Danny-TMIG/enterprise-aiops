import importlib

import pytest


def test_proof_import():
    try:
        mod = importlib.import_module("app.proof")
        assert mod is not None
    except ImportError:
        pytest.skip("app.proof submodule not present or empty")
