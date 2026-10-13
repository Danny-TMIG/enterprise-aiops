"""Catch-and-release error handling. Parse tracebacks, emit records, never re-raise."""
from __future__ import annotations

import asyncio
import traceback
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from functools import wraps
from threading import Lock
from typing import Any

_CLASSIFIERS = [
    ("shadow",      lambda e: isinstance(e, ImportError) and "cannot import name" in str(e)),
    ("missing_dep", lambda e: isinstance(e, ModuleNotFoundError)),
    ("shape",       lambda e: isinstance(e, AttributeError) and "has no attribute" in str(e)),
    ("shape",       lambda e: isinstance(e, TypeError) and "positional argument" in str(e)),
    ("shape",       lambda e: isinstance(e, TypeError) and "not iterable" in str(e)),
    ("key",         lambda e: isinstance(e, KeyError)),
    ("assert",      lambda e: isinstance(e, AssertionError)),
    ("syntax",      lambda e: isinstance(e, SyntaxError)),
    ("fs",          lambda e: isinstance(e, (IsADirectoryError, FileNotFoundError, PermissionError))),
    ("index",       lambda e: isinstance(e, IndexError)),
    ("value",       lambda e: isinstance(e, ValueError)),
    ("runtime",     lambda e: isinstance(e, RuntimeError)),
    ("io",          lambda e: isinstance(e, OSError)),
]

@dataclass(frozen=True)
class Frame:
    file: str; line: int; func: str; source: str = ""

@dataclass
class Catch:
    id: str; when: str; kind: str; category: str; message: str
    frames: list[Frame]; origin: str; released: bool = False
    meta: dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> dict[str, Any]: return asdict(self)

def _origin(frames):
    ours = [f for f in frames if "/site-packages/" not in f.file and "/.venv/" not in f.file]
    f = (ours or frames or [Frame("<unknown>", 0, "<module>")])[-1]
    return f"{f.file}:{f.line}:{f.func}"

def _classify(exc):
    for name, test in _CLASSIFIERS:
        try:
            if test(exc): return name
        except Exception: pass
    return "other"

def parse(exc, *, meta=None):
    frames = [Frame(fs.filename, fs.lineno, fs.name, (fs.line or "").strip())
              for fs in traceback.extract_tb(exc.__traceback__)]
    return Catch(uuid.uuid4().hex[:12], datetime.now(timezone.utc).isoformat(),
                 type(exc).__name__, _classify(exc), str(exc),
                 frames, _origin(frames), False, meta or {})

_BUFFER: deque[Catch] = deque(maxlen=500)
_LOCK = Lock()

def release(catch):
    catch.released = True
    with _LOCK: _BUFFER.append(catch)
    return catch

def recent(limit=50, category=None):
    with _LOCK: items = list(_BUFFER)
    if category: items = [c for c in items if c.category == category]
    return [c.to_dict() for c in items[-limit:]]

def counts():
    with _LOCK: items = list(_BUFFER)
    out = {}
    for c in items: out[c.category] = out.get(c.category, 0) + 1
    return out

def catch_and_release(fallback=None, *, reraise=False, meta=None):
    def deco(fn):
        if asyncio.iscoroutinefunction(fn):
            @wraps(fn)
            async def awrap(*a, **k):
                try: return await fn(*a, **k)
                except BaseException as e:
                    release(parse(e, meta={**(meta or {}), "fn": fn.__qualname__}))
                    if reraise: raise
                    return fallback
            return awrap
        @wraps(fn)
        def wrap(*a, **k):
            try: return fn(*a, **k)
            except BaseException as e:
                release(parse(e, meta={**(meta or {}), "fn": fn.__qualname__}))
                if reraise: raise
                return fallback
        return wrap
    return deco

class catcher:
    def __init__(self, fallback=None, *, reraise=False, meta=None):
        self.fallback = fallback; self.reraise = reraise; self.meta = meta or {}; self.catch = None
    def __enter__(self): return self
    def __exit__(self, et, e, tb):
        if e is None: return False
        self.catch = parse(e, meta=self.meta); release(self.catch)
        return False if self.reraise else True

def install_middleware(app):
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse
    class CatchRelease(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            try: return await call_next(request)
            except BaseException as e:
                c = parse(e, meta={"method": request.method, "path": str(request.url.path)})
                release(c)
                return JSONResponse(status_code=500, content={"released": True, "catch": c.to_dict()})
    app.add_middleware(CatchRelease)

def install_routes(app):
    @app.get("/diag/catches")
    def _catches(limit: int = 50, category: str | None = None):
        return {"catches": recent(limit=limit, category=category)}
    @app.get("/diag/catches/counts")
    def _counts(): return {"counts": counts()}

def install(app):
    install_middleware(app); install_routes(app)

__all__ = [
    "Catch",
    "Frame",
    "catch_and_release",
    "catcher",
    "counts",
    "install",
    "install_middleware",
    "install_routes",
    "parse",
    "recent",
    "release",
]


# ── self-registration: this module is a capability of the fabric ──
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("catch_release")
    def _entrypoint(*args, **kwargs):
        """Dispatch entry: return module metadata + recent catch count."""
        return {
            "module": "app.core.catch_release",
            "recent": len(recent(limit=1)),
            "counts": counts(),
        }


_self_register()
