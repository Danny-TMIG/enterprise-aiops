from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import hashlib, time

app = FastAPI(title="Aether Sovereign Fabric API", version="1.1.0")

class IR(BaseModel):
    ir_version: str = "1.1.0"
    source_identifier: str
    opcode: str
    taxonomy_target: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class Envelope(BaseModel):
    payload: IR
    checksum_signature: str
    timestamp: float = Field(default_factory=time.time)

@app.get("/health")
def health(): return {"status": "HEALTHY", "fabric": "ASF v1.1", "hardware": "Apple M4 Max (Mac16,5)"}

@app.post("/v1/execute")
def execute(env: Envelope):
    calc_hash = hashlib.sha256(env.payload.model_dump_json().encode()).hexdigest()
    if env.checksum_signature != calc_hash:
        raise HTTPException(status_code=400, detail="State verification failed.")
    return {"status": "EXECUTED", "checksum": calc_hash}
