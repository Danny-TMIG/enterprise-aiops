from __future__ import annotations
from typing import Optional

from app.murmur.flock import Flock


_RT: Optional[Flock] = None


def get_flock(n: int = 8) -> Flock:
    global _RT
    if _RT is None:
        _RT = Flock(n=n)
    return _RT


def reset() -> None:
    global _RT
    _RT = None
