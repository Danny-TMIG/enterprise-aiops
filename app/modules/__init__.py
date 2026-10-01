"""Module registry.

Every known source of modules, in one place. Not every module — that
number is >10 million and grows hourly. The *sources* are enumerable;
the *contents* are queried on demand.

    ECOSYSTEMS  — 15 major package ecosystems, each with index URL
    fetch(name) — pull a real package list from a network index
    lookup(pkg) — one package's metadata (version, deps, home)
    local()     — every module already importable in this process
    tree()      — the fabric's own module tree
"""
from __future__ import annotations
import importlib, importlib.metadata, json, sys, urllib.request
from typing import Any, Dict, Iterable, List, Optional

# ── the 15 major ecosystems ─────────────────────────────────────
ECOSYSTEMS: Dict[str, Dict[str, str]] = {
    "pypi":     {"lang": "python",  "index": "https://pypi.org/pypi",
                 "list_api": "https://pypi.org/simple/",
                 "count_est": "~530k"},
    "npm":      {"lang": "js/ts",   "index": "https://registry.npmjs.org",
                 "list_api": "https://registry.npmjs.org/-/v1/search",
                 "count_est": "~3.4M"},
    "crates":   {"lang": "rust",    "index": "https://crates.io/api/v1/crates",
                 "list_api": "https://crates.io/api/v1/crates",
                 "count_est": "~160k"},
    "go":       {"lang": "go",      "index": "https://proxy.golang.org",
                 "list_api": "https://index.golang.org/index",
                 "count_est": "~1.5M"},
    "maven":    {"lang": "java",    "index": "https://search.maven.org",
                 "list_api": "https://search.maven.org/solrsearch/select",
                 "count_est": "~600k"},
    "rubygems": {"lang": "ruby",    "index": "https://rubygems.org/api/v1",
                 "list_api": "https://rubygems.org/api/v1/search.json",
                 "count_est": "~180k"},
    "hex":      {"lang": "erlang",  "index": "https://hex.pm/api",
                 "list_api": "https://hex.pm/api/packages",
                 "count_est": "~18k"},
    "pub":      {"lang": "dart",    "index": "https://pub.dev/api",
                 "list_api": "https://pub.dev/api/packages",
                 "count_est": "~50k"},
    "cocoapods":{"lang": "swift",   "index": "https://cocoapods.org",
                 "list_api": "https://trunk.cocoapods.org/api/v1/pods",
                 "count_est": "~100k"},
    "nuget":    {"lang": "dotnet",  "index": "https://api.nuget.org/v3",
                 "list_api": "https://api.nuget.org/v3/registration5-semver1",
                 "count_est": "~400k"},
    "conda":    {"lang": "python",  "index": "https://conda.anaconda.org",
                 "list_api": "https://api.anaconda.org/search",
                 "count_est": "~40k"},
    "hackage":  {"lang": "haskell", "index": "https://hackage.haskell.org",
                 "list_api": "https://hackage.haskell.org/packages/",
                 "count_est": "~18k"},
    "opam":     {"lang": "ocaml",   "index": "https://opam.ocaml.org",
                 "list_api": "https://opam.ocaml.org/packages/",
                 "count_est": "~4k"},
    "ctan":     {"lang": "tex",     "index": "https://ctan.org/json",
                 "list_api": "https://ctan.org/json/2.0/packages",
                 "count_est": "~6k"},
    "cpan":     {"lang": "perl",    "index": "https://metacpan.org",
                 "list_api": "https://fastapi.metacpan.org/v1/release/_search",
                 "count_est": "~220k"},
}


# ── query ────────────────────────────────────────────────────────
def lookup(pkg: str, *, ecosystem: str = "pypi",
           timeout: float = 10.0) -> Optional[Dict[str, Any]]:
    """One package's metadata from its ecosystem's index."""
    eco = ECOSYSTEMS.get(ecosystem)
    if not eco:
        return None
    if ecosystem == "pypi":
        url = f"{eco['index']}/{pkg}/json"
    elif ecosystem == "npm":
        url = f"{eco['index']}/{pkg}"
    elif ecosystem == "crates":
        url = f"{eco['index']}/{pkg}"
    else:
        return None  # only the three with stable single-package JSON
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e), "url": url}


def fetch(query: str, *, ecosystem: str = "npm",
          limit: int = 20, timeout: float = 10.0
          ) -> List[Dict[str, Any]]:
    """Search an ecosystem for `query`. Returns list of hits."""
    eco = ECOSYSTEMS.get(ecosystem) or {}
    if ecosystem == "npm":
        url = f"{eco['list_api']}?text={query}&size={limit}"
    elif ecosystem == "crates":
        url = f"{eco['list_api']}?q={query}&per_page={limit}"
    elif ecosystem == "pypi":
        # PyPI's simple index is a 30 MB HTML page; use search-suggest
        url = f"https://pypi.org/pypi/{query}/json"
    else:
        return []
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.loads(r.read().decode())
        if ecosystem == "npm":
            return [{"name": o["package"]["name"],
                     "version": o["package"]["version"],
                     "desc": o["package"].get("description", "")}
                    for o in data.get("objects", [])][:limit]
        if ecosystem == "crates":
            return [{"name": c["name"], "version": c.get("max_version", "")}
                    for c in data.get("crates", [])][:limit]
        if ecosystem == "pypi":
            info = data.get("info", {})
            return [{"name": info.get("name"), "version": info.get("version"),
                     "desc": (info.get("summary") or "")[:100]}]
    except Exception:
        return []
    return []


# ── local: every module already importable in this process ───────
def local() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for m in importlib.metadata.distributions():
        try:
            out.append({"name": m.metadata["Name"],
                        "version": m.version,
                        "summary": (m.metadata.get("Summary") or "")[:80]})
        except Exception:
            continue
    return sorted(out, key=lambda x: (x["name"] or "").lower())


# ── the fabric's own module tree ─────────────────────────────────
def tree(root: Optional[str] = None) -> Dict[str, Any]:
    import ast
    from pathlib import Path
    base = Path(root) if root else Path(__file__).resolve().parent.parent
    out: Dict[str, Any] = {}
    for p in sorted(base.rglob("*.py")):
        if "__pycache__" in str(p):
            continue
        try:
            t = ast.parse(p.read_text())
        except Exception:
            continue
        names = [n.name for n in t.body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        if names:
            out[str(p.relative_to(base))] = names
    return out


# ── self-registration ────────────────────────────────────────────
def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("modules")
    def _entry(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {
            "ecosystems": {k: v["count_est"] for k, v in ECOSYSTEMS.items()},
            "installed": len(local()),
            "local_tree_files": len(tree()),
        }


_self_register()

__all__ = ["ECOSYSTEMS", "lookup", "fetch", "local", "tree"]
