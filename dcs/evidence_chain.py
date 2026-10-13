# Invariant Evidence Chain Module
import hashlib, hmac, json
from pathlib import Path
from typing import Dict, Any

SIGNING_KEY = b"sovereign_secret_key_2026"

def calculate_file_hash(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists(): return hashlib.sha256(b"").hexdigest()
    with open(path, "rb") as f: return hashlib.sha256(f.read()).hexdigest()

def generate_evidence_claim(proc_id: str, impl_file: str, test_file: str, cmd_output: str, return_code: int) -> Dict[str, Any]:
    impl_hash = calculate_file_hash(impl_file)
    test_hash = calculate_file_hash(test_file)
    stdout_hash = hashlib.sha256(cmd_output.encode("utf-8")).hexdigest()
    payload = f"{proc_id}:{impl_hash}:{test_hash}:{stdout_hash}:{return_code}"
    signature = hmac.new(SIGNING_KEY, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return {"process_id": proc_id, "implementation_hash": impl_hash, "test_hash": test_hash, "stdout_hash": stdout_hash, "return_code": return_code, "signature": signature}

def verify_evidence_claim(record: Dict[str, Any], fresh_output: str, fresh_rc: int, fresh_impl_hash: str = None) -> str:
    payload = f"{record["process_id"]}:{record["implementation_hash"]}:{record["test_hash"]}:{record["stdout_hash"]}:{record["return_code"]}"
    if not hmac.compare_digest(record.get("signature", ""), hmac.new(SIGNING_KEY, payload.encode("utf-8"), hashlib.sha256).hexdigest()): return "BLOCKED"
    current_impl_hash = fresh_impl_hash if fresh_impl_hash else record["implementation_hash"]
    if current_impl_hash != record["implementation_hash"]: return "PARTIAL"
    if hashlib.sha256(fresh_output.encode("utf-8")).hexdigest() == record["stdout_hash"] and fresh_rc == record["return_code"]: return "PASS"
    return "BLOCKED"
# Result constants. verify_evidence_claim returns one of these strings.
PASS = "PASS"
PARTIAL = "PARTIAL"
BLOCKED = "BLOCKED"
