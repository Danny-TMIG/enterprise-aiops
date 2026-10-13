# Invariant Evidence Verification Program
import subprocess
from dcs.evidence_chain import verify_evidence_claim
def re_verify_record(record: dict, command: list, current_impl_file: str) -> str:
    try:
        res = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return verify_evidence_claim(record, res.stdout, res.returncode)
    except Exception as e: return verify_evidence_claim(record, str(e), -1)