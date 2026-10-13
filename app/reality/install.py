"""Install plan. Network operations require AIOPS_ALLOW_NETWORK=1."""
from __future__ import annotations

import os
import shutil
from typing import Any

INSTALLABLE = {
    "codeql": {
        "check": lambda: bool(shutil.which("codeql")
                              or os.path.exists(os.path.expanduser(
                                  "~/.codeql/codeql"))),
        "how": "download CodeQL bundle from github.com/github/codeql-action/releases",
        "network": True,
    },
    "lean": {
        "check": lambda: shutil.which("lean") is not None,
        "how": "curl https://elan.lean-lang.org/elan-init.sh -sSf | sh -s -- -y",
        "network": True,
    },
    "lean_dojo": {
        "check": lambda: _mod("lean_dojo"),
        "how": "pip install lean_dojo",
        "network": True,
    },
}


def _mod(name: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(name) is not None


def install_local(allow_network: bool = False) -> list[dict[str, Any]]:
    out = []
    for name, spec in INSTALLABLE.items():
        present = bool(spec["check"]())
        if present:
            out.append({"name": name, "present": True,
                        "action": "already installed"})
            continue
        if spec["network"] and not allow_network:
            out.append({"name": name, "present": False,
                        "action": "blocked (set AIOPS_ALLOW_NETWORK=1)",
                        "how": spec["how"]})
            continue
        out.append({"name": name, "present": False,
                    "action": "run manually",
                    "how": spec["how"]})
    return out
