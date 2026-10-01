import sys
import pytest

@pytest.fixture(autouse=True)
def _isolate_cli_args(monkeypatch):
    """Automatically isolate sys.argv during tests to prevent argparse from parsing pytest arguments."""
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
