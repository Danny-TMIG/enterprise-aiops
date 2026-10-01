from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Histogram,
    generate_latest,
)


def _get_or_create_histogram(
    name, documentation, labelnames=(), buckets=Histogram.DEFAULT_BUCKETS
):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Histogram(name, documentation, labelnames=labelnames, buckets=buckets)


def _get_or_create_counter(name, documentation, labelnames=()):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, documentation, labelnames=labelnames)


import signal
import sys

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

from app.moa_cluster import MoAOrchestrator

app = FastAPI(title="MLX MoE/MoA Enterprise Engine", version="1.0.0")
orchestrator = MoAOrchestrator()

REQUEST_COUNT = _get_or_create_counter("engine_requests", "Engine Requests")

REQUEST_LATENCY = _get_or_create_histogram(
    "engine_request_latency_seconds", "Request latency", ["endpoint"]
)

is_shutting_down = False


def handle_sigterm(signum: int, frame: object) -> None:
    global is_shutting_down
    is_shutting_down = True
    print("SIGTERM received. Graceful shutdown initiated...", file=sys.stderr)


signal.signal(signal.SIGTERM, handle_sigterm)


class DocumentRequest(BaseModel):
    document_text: str
    layout_metadata: dict


@app.get("/health/live", response_model=None)
async def liveness_probe() -> dict:
    if is_shutting_down:
        return Response(status_code=503, content="Shutting down")  # type: ignore[return-value]
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_probe() -> dict:
    if is_shutting_down or orchestrator is None:
        return Response(status_code=503, content="Not ready")  # type: ignore[return-value]
    return {"status": "ready"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/moa/extract")
async def extract_document(req: DocumentRequest) -> dict:
    try:
        result = await orchestrator.process_request(
            document_text=req.document_text,
            layout_metadata=req.layout_metadata,
        )
        return {"status": "success", "extracted_payload": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
