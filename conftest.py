"""Root conftest: shared CLI options, hooks, and session fixtures."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False,
                     help="run tests marked slow")
    parser.addoption("--runintegration", action="store_true", default=False,
                     help="run tests marked integration")


def pytest_collection_modifyitems(config, items):
    skip_slow = pytest.mark.skip(reason="needs --runslow")
    skip_int = pytest.mark.skip(reason="needs --runintegration")
    for item in items:
        if "slow" in item.keywords and not config.getoption("runslow"):
            item.add_marker(skip_slow)
        if "integration" in item.keywords and not config.getoption("runintegration"):
            item.add_marker(skip_int)


def pytest_report_header(config):
    return [
        "repo:        " + str(REPO_ROOT),
        "python:      " + sys.version.split()[0],
        "venv:        " + str(VENV_PYTHON.exists()),
        "runslow:     " + str(config.getoption("runslow")),
        "integration: " + str(config.getoption("runintegration")),
    ]


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def venv_python():
    if not VENV_PYTHON.exists():
        pytest.skip("no .venv/bin/python")
    return VENV_PYTHON


@pytest.fixture(scope="session")
def run_cmd(venv_python):
    """Run a command; fail with captured output on nonzero."""
    def _run(args, cwd=REPO_ROOT, timeout=60, check=True, env=None):
        argv = [str(a) for a in args]
        r = subprocess.run(
            argv, cwd=str(cwd),
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, **(env or {})},
        )
        if check and r.returncode != 0:
            msg = (
                "cmd failed: " + " ".join(argv) + "\n"
                + "rc=" + str(r.returncode) + "\n"
                + "stdout=" + r.stdout[-2000:] + "\n"
                + "stderr=" + r.stderr[-2000:]
            )
            pytest.fail(msg)
        return r
    return _run
