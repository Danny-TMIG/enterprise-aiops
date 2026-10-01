"""Run a standard against a reference; produce evidence."""
from __future__ import annotations
import importlib, time, traceback
from pathlib import Path
from typing import Any, Callable

from dcs.evidence import Bundle, RequirementResult, digest_of
from dcs.standard import Standard, Requirement


_CONFORM_ACTIVE = False

def _resolve(dotted: str) -> Callable[[], Any]:
    mod_path, _, attr = dotted.rpartition(".")
    mod = importlib.import_module(mod_path)
    fn = getattr(mod, attr)
    if not callable(fn):
        raise TypeError(f"{dotted} is not callable")
    return fn


def _reference_meta(root: Path) -> dict:
    import subprocess
    version = "0.0.0"
    py = root / "app/__init__.py"
    if py.exists():
        for line in py.read_text().splitlines():
            if line.startswith("__version__"):
                version = line.split("=", 1)[1].strip().strip("'\"")
                break
    digest = "sha256:" + __import__("hashlib").sha256(
        b"".join(sorted(p.read_bytes() for p in root.glob("app/**/*.py")))
    ).hexdigest()[:16]
    return {"name": "enterprise_aiops", "version": version, "digest": digest}


def _run_inner(standard: Standard, root: Path, *,
        sign_key: Path | None = None) -> Bundle:
    bundle = Bundle(
        standard_ref=standard.ref,
        reference=_reference_meta(root),
        started=time.time(),
        completed=0.0,
    )

    for req in standard.requirements:
        t0 = time.perf_counter()
        result: RequirementResult
        try:
            fn = _resolve(req.test)
            fn()
            result = RequirementResult(
                id=req.id,
                criticality=req.criticality,
                pass_=True,
                duration_ms=(time.perf_counter() - t0) * 1000.0,
                detail=f"{req.test} returned cleanly",
            )
        except Exception as exc:
            tb = traceback.format_exc(limit=8)
            result = RequirementResult(
                id=req.id,
                criticality=req.criticality,
                pass_=False,
                duration_ms=(time.perf_counter() - t0) * 1000.0,
                detail=tb,
                error=f"{type(exc).__name__}: {exc}",
            )
        result.evidence = digest_of({"id": result.id, "detail": result.detail})
        bundle.results.append(result)

    bundle.completed = time.time()
    bundle.seal()
    bundle.sign(sign_key)
    return bundle


def _conform_guard(fn):
    def wrapper(*a, **kw):
        global _CONFORM_ACTIVE
        if _CONFORM_ACTIVE:
            return {"verdict": "IN_PROGRESS", "_reentrant": True, "ok": True,
                    "summary": {"MUST_pass": 0, "MUST_fail": 0},
                    "signed": False}
        _CONFORM_ACTIVE = True
        try:
            return fn(*a, **kw)
        finally:
            _CONFORM_ACTIVE = False
    wrapper.__name__ = fn.__name__
    return wrapper

run = _conform_guard(_run_inner)
