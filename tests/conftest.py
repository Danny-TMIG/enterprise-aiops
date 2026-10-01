
import multiprocessing
try:
    multiprocessing.set_start_method("spawn", force=True)
except RuntimeError:
    pass

import sys
import pytest

@pytest.fixture(autouse=True)
def _isolate_cli_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
