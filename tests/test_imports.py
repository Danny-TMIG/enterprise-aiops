"""Import every component's src.public package, one subprocess per component."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _component_dirs(repo_root: Path) -> list[Path]:
    out = []
    for layer in ("ax", "ag", "ac"):
        layer_dir = repo_root / "components" / layer
        if not layer_dir.is_dir():
            continue
        for comp in sorted(layer_dir.iterdir()):
            if not comp.is_dir():
                continue
            if comp.name.startswith("_") or comp.name.startswith("."):
                continue
            if (comp / "src" / "public" / "__init__.py").is_file():
                out.append(comp)
    return out


def _try_import(component: Path) -> tuple[bool, str, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
    code = (
        "import sys, importlib; "
        "sys.path.insert(0, '.'); "
        "importlib.import_module('src.public'); "
        "print('OK')"
    )
    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(component.resolve()),
            capture_output=True, text=True, timeout=30, env=env,
        )
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    return (r.returncode == 0 and r.stdout.strip() == "OK"), r.stdout, r.stderr


def test_import_each_component(repo_root):
    failures = []
    for comp in _component_dirs(repo_root):
        ok, out, err = _try_import(comp)
        if not ok:
            failures.append(
                f"{comp.name}:\n"
                f"  stdout: {out!r}\n"
                f"  stderr: {err!r}"
            )
    assert not failures, (
        f"{len(failures)} import failures:\n" + "\n".join(failures[:3])
    )
