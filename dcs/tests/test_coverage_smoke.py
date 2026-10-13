"""Import-only smoke test. Regenerate after refactors."""
import importlib
import pytest


@pytest.mark.parametrize("name", ["dcs.coherence"])
def test_import(name):
    importlib.import_module(name)
