#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_BIN = ROOT / ".venv" / "bin"

PYTHON = VENV_BIN / "python"
PYTEST = VENV_BIN / "pytest"
RUFF = VENV_BIN / "ruff"
MYPY = VENV_BIN / "mypy"

def run_step(name: str, cmd: list[str]) -> None:
    print(f"==> Running step: {name}")
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        print(f"Error: Step '{name}' failed with code {result.returncode}")
        sys.exit(result.returncode)

def main() -> None:
    if not PYTHON.exists():
        print("Error: Virtual environment not found. Run 'make setup' first.")
        sys.exit(1)

    run_step("ruff fix", [str(RUFF), "check", "--fix", "."])
    run_step("mypy", [str(MYPY), "app", "tests"])
    run_step("pytest", [str(PYTEST), "-v"])
    print("==> All verification checks passed cleanly.")

if __name__ == "__main__":
    main()
