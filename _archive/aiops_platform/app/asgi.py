from __future__ import annotations

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
    return {
        "service": "aiops_platform",
        "merkle_root": _engine.merkle_root(),
        "patches": len(_engine.history()),
    }


def main() -> None:
    uvicorn.run("aiops_platform.app.asgi:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
