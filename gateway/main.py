from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from gateway.config import settings

app = FastAPI(title=settings.app_name, version=settings.version)

@app.get("/health")
async def health_check():
    return {"status": "operational", "version": settings.version, "app": settings.app_name}

@app.post("/v1/completions")
async def completions(request: Request):
    body = await request.json()
    headers = request.headers
    prompt = body.get("prompt", "")

    # Check for CISO Veto / System Override block
    if headers.get("X-CISO-Veto") == "active" or body.get("veto") == "ciso" or "system_override" in prompt.lower():
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "CISO_SECURITY_VETO",
                    "message": "Blocked by CISO executive veto gate."
                }
            }
        )

    return {
        "id": "cmpl-sovereign-1",
        "object": "text_completion",
        "model": "qwen2.5-7b-instruct",
        "choices": [{"text": "Sovereign inference execution successful.", "index": 0}]
    }
