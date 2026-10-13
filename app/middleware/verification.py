import hashlib
import time

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class EnterpriseStateEngine:
    def __init__(self):
        self.locked = False
        self.owner = None
        self.corpus_registry: set[str] = set()
        self.last_transition = time.time()

    def acquire(self, client_id: str) -> bool:
        if self.locked and self.owner != client_id: return False
        self.locked = True
        self.owner = client_id
        return True

    def release(self, client_id: str) -> bool:
        if self.locked and self.owner == client_id:
            self.locked = False
            self.owner = None
            return True
        return False

    def verify_corpus(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

engine = EnterpriseStateEngine()

class VerificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in ["POST", "PUT", "DELETE"] and "/state/" in request.url.path:
            client_id = request.headers.get("X-Agent-ID")
            if not client_id:
                raise HTTPException(status_code=400, detail="Missing X-Agent-ID header.")
            if not engine.locked: engine.acquire(client_id)
            elif engine.owner != client_id:
                raise HTTPException(status_code=409, detail=f"Locked by active owner: {engine.owner}")
        return await call_next(request)
