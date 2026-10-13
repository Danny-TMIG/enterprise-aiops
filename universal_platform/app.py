from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from dcs.core.difference_engine import ParallelDifferenceEngine

app = FastAPI(title="Universal Platform Parallel Difference Engine API", version="2.0.0")

class AuditPayload(BaseModel):
    processes: List[Dict[str, Any]]

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "engine": "PARALLEL_DIFFERENCE_CORE"}

@app.post("/api/v1/audit")
def trigger_parallel_audit(payload: AuditPayload):
    if not payload.processes:
        raise HTTPException(status_code=400, detail="Empty compliance tracking process block.")
    engine = ParallelDifferenceEngine()
    audit_results = engine.execute_parallel_audit(payload.processes)
    failed_count = sum(1 for r in audit_results if r["variance_detected"])
    compliance_score = ((len(audit_results) - failed_count) / len(audit_results)) * 100
    return {
        "status": "COMPLETED",
        "compliance_score_percentage": compliance_score,
        "results_matrix": audit_results
    }
