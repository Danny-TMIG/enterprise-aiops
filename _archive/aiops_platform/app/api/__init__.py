from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "aiops_platform"}


@router.get("/version")
def version() -> dict:
    from aiops_platform import __version__

    return {"version": __version__}
