import shutil
import subprocess
import textwrap
from pathlib import Path

ROOT = Path.cwd()


def W(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content).lstrip())
    print("wrote", path)


W(
    ".gitignore",
    "__pycache__/\n*.py[cod]\n.venv/\nvenv/\nenv/\n.lanes/\nbuild/\ndist/\n*.egg-info/\n*.db\n*.sqlite\n*.sqlite3\n.DS_Store\n.idea/\n.vscode/\n.env\n.env.*\n!.env.example\n_site/\n_jekyll_site/\n.pytest_cache/\n.mypy_cache/\n.ruff_cache/\n*.log\n",
)

W("requirements.txt", "fastapi>=0.110\nuvicorn[standard]>=0.29\npydantic>=2.6\n")

W(
    "requirements-dev.txt",
    "-r requirements.txt\npytest>=8.0\npytest-asyncio>=0.23\nhttpx>=0.27\nruff>=0.4\nmypy>=1.10\n",
)

W(
    "pyproject.toml",
    """[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "aiops-platform"
version = "1.0.0"
description = "Sovereign local-first AIOps platform"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = ["fastapi>=0.110", "uvicorn[standard]>=0.29", "pydantic>=2.6"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "httpx>=0.27", "ruff>=0.4", "mypy>=1.10"]

[project.scripts]
aiops-serve = "aiops_platform.app.asgi:main"

[tool.setuptools.packages.find]
include = ["aiops_platform*"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
""",
)

W(
    "LICENSE",
    """MIT License

Copyright (c) 2026 Sovereign Stack

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
)

W(
    "README.md",
    """# aiops_platform

Sovereign local-first AIOps platform. FastAPI ASGI app, SQLite ledger,
and versioned engine patches with Merkle-rooted history.

## Quickstart

    git clone <this-repo> aiops_platform
    cd aiops_platform
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python3 -m aiops_platform.app.asgi

Then in another terminal:

    curl -sS http://127.0.0.1:8000/health
    curl -sS http://127.0.0.1:8000/

Expected:

    {"status":"ok","service":"aiops_platform"}
    {"service":"aiops_platform","merkle_root":"<64 hex>","patches":1}

## Layout

    aiops_platform/
      __init__.py
      app/
        __init__.py
        asgi.py
        api/__init__.py
        core/engine_patch.py
        db/__init__.py

## Design notes

Never name a package after a stdlib module. This repo previously had a
platform/ package that shadowed the stdlib and broke pandas, numpy,
pytest, pip, and uvicorn for any process running from the repo root.

## License

MIT. See LICENSE.
""",
)

W(
    "CONTRIBUTING.md",
    """# Contributing

## Setup

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    pip install -e .

## Checks

    ruff check .
    mypy aiops_platform
    pytest -q
""",
)

W(
    "CHANGELOG.md",
    """# Changelog

## [Unreleased]

## [1.0.0] - 2026-10-13

### Added
- aiops_platform package with ASGI entrypoint
- SovereignEnginePatch primitive with Merkle-rooted patch history
- SQLite event log
- REST endpoints /health, /version, /
- pytest suite

### Fixed
- Renamed platform/ to aiops_platform/ to stop shadowing the Python
  stdlib platform module.
""",
)

W(
    ".env.example",
    "AIOPS_HOST=127.0.0.1\nAIOPS_PORT=8000\nAIOPS_LOG_LEVEL=info\nAIOPS_DB_PATH=aiops.db\n",
)

W(
    "Makefile",
    """.PHONY: help install dev test lint type fmt serve clean

help:
	@echo "install dev test lint type fmt serve clean"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest -q

lint:
	ruff check .

type:
	mypy aiops_platform

fmt:
	ruff format .

serve:
	python3 -m aiops_platform.app.asgi

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
""",
)

W("tests/__init__.py", "")
W(
    "tests/conftest.py",
    """import pytest
from fastapi.testclient import TestClient
from aiops_platform.app.asgi import app

@pytest.fixture
def client():
    return TestClient(app)
""",
)
W(
    "tests/test_api.py",
    """def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_version(client):
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json()["version"] == "1.0.0"

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "aiops_platform"
    assert len(body["merkle_root"]) == 64
    assert body["patches"] >= 1
""",
)
W(
    "tests/test_engine_patch.py",
    """from aiops_platform.app.core.engine_patch import SovereignEnginePatch

def test_apply_and_history():
    eng = SovereignEnginePatch()
    assert eng.history() == []
    eng.apply("boot", {"stage": "test"})
    assert len(eng.history()) == 1

def test_merkle_root_is_stable():
    a = SovereignEnginePatch(); a.apply("x", {"n": 1})
    b = SovereignEnginePatch(); b.apply("x", {"n": 1})
    assert a.merkle_root() == b.merkle_root()

def test_merkle_root_changes():
    a = SovereignEnginePatch(); a.apply("x", {"n": 1})
    b = SovereignEnginePatch(); b.apply("x", {"n": 2})
    assert a.merkle_root() != b.merkle_root()
""",
)

W("scripts/__init__.py", "")
W(
    "scripts/smoke.py",
    """import subprocess, sys, time, urllib.request

def main():
    proc = subprocess.Popen(
        [sys.executable, "-m", "aiops_platform.app.asgi"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(2)
        for url in ("http://127.0.0.1:8000/health", "http://127.0.0.1:8000/"):
            with urllib.request.urlopen(url, timeout=3) as r:
                print(url, "->", r.read().decode())
        return 0
    finally:
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == "__main__":
    raise SystemExit(main())
""",
)

W("docs/index.md", "# aiops_platform docs\n\n- architecture.md\n- api.md\n- operations.md\n")
W(
    "docs/architecture.md",
    "# Architecture\n\nFastAPI app wired in aiops_platform/app/asgi.py. Router in app/api. Patch primitive in app/core/engine_patch.py. SQLite in app/db.\n",
)
W(
    "docs/api.md",
    "# API\n\nGET /health -> liveness\n\nGET /version -> package version\n\nGET / -> service metadata and Merkle root\n",
)
W(
    "docs/operations.md",
    "# Operations\n\nStart:\n\n    python3 -m aiops_platform.app.asgi\n\nKill port 8000:\n\n    lsof -ti:8000 | xargs -r kill -9\n",
)

W(
    ".editorconfig",
    "root = true\n\n[*]\ncharset = utf-8\nend_of_line = lf\ninsert_final_newline = true\ntrim_trailing_whitespace = true\nindent_style = space\nindent_size = 4\n\n[*.{yml,yaml,json,toml}]\nindent_size = 2\n\n[Makefile]\nindent_style = tab\n",
)

W(
    ".pre-commit-config.yaml",
    """repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
""",
)

PKG = ROOT / "aiops_platform"
for sub in ("app", "app/core", "app/api", "app/db"):
    (PKG / sub).mkdir(parents=True, exist_ok=True)

W("aiops_platform/__init__.py", '__version__ = "1.0.0"\n')
W("aiops_platform/app/__init__.py", "")
W("aiops_platform/app/core/__init__.py", "")
W(
    "aiops_platform/app/core/engine_patch.py",
    """from __future__ import annotations
import hashlib, json, time
from dataclasses import dataclass, field, asdict

@dataclass
class PatchRecord:
    name: str
    version: str = "1.0.0"
    applied_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    payload: dict = field(default_factory=dict)
    def digest(self) -> str:
        canon = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canon.encode()).hexdigest()

class SovereignEnginePatch:
    def __init__(self) -> None:
        self._applied: list[PatchRecord] = []
    def apply(self, name: str, payload: dict | None = None) -> PatchRecord:
        rec = PatchRecord(name=name, payload=payload or {})
        self._applied.append(rec)
        return rec
    def history(self) -> list[PatchRecord]:
        return list(self._applied)
    def merkle_root(self) -> str:
        if not self._applied:
            return hashlib.sha256(b"empty").hexdigest()
        h = hashlib.sha256()
        for r in self._applied:
            h.update(r.digest().encode())
        return h.hexdigest()
""",
)
W(
    "aiops_platform/app/db/__init__.py",
    '''from __future__ import annotations
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "aiops.db"

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, kind TEXT, payload TEXT, digest TEXT)""")
    conn.commit()
    return conn
''',
)
W(
    "aiops_platform/app/api/__init__.py",
    """from __future__ import annotations
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "aiops_platform"}

@router.get("/version")
def version() -> dict:
    from aiops_platform import __version__
    return {"version": __version__}
""",
)
W(
    "aiops_platform/app/asgi.py",
    """from __future__ import annotations
import uvicorn
from fastapi import FastAPI
from aiops_platform.app.api import router
from aiops_platform.app.core.engine_patch import SovereignEnginePatch

app = FastAPI(title="AIOps Platform", version="1.0.0")
app.include_router(router)

_engine = SovereignEnginePatch()
_engine.apply("bootstrap", {"stage": "asgi-import"})

@app.get("/")
def root() -> dict:
    return {"service": "aiops_platform", "merkle_root": _engine.merkle_root(), "patches": len(_engine.history())}

def main() -> None:
    uvicorn.run("aiops_platform.app.asgi:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
""",
)

scaffold = ROOT / "scaffold_enterprise_suite.py"
if scaffold.exists():
    t = scaffold.read_text()
    n = t.replace("from platform.app.", "from aiops_platform.app.").replace(
        "import platform.app.", "import aiops_platform.app."
    )
    if n != t:
        scaffold.write_text(n)
        print("patched scaffold_enterprise_suite.py")

for name in (
    "fix_test_imports.py",
    "fix_final_imports.py",
    "fix_imports_and_packages.py",
    "fix_imports.py",
):
    p = ROOT / name
    if p.exists():
        p.unlink()
        print("removed", name)

for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

if not (ROOT / ".git").exists():
    subprocess.run(["git", "init", "-b", "main"], cwd=ROOT, check=False)
    print("git init")

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
lines = r.stdout.splitlines()
print(f"\ngit status: {len(lines)} entries")
for l in lines[:40]:
    print(" ", l)
leaked = [l for l in lines if ".venv/" in l or ".lanes/" in l or l.endswith(".db")]
print("\nleaked:", leaked[:5] if leaked else "none")

print("\nDone. Publish with:")
print("  git commit -m 'Initial commit: aiops_platform'")
print("  gh repo create aiops_platform --public --source=. --push")
