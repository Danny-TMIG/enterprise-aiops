# Invariant Evidence Qualification Program
import subprocess
from dcs.evidence_chain import generate_evidence_claim
def qualify_process(proc_id: str, command: list, impl_file: str, test_file: str) -> dict:
    try:
        res = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return generate_evidence_claim(proc_id, impl_file, test_file, res.stdout, res.returncode)
    except Exception as e: return generate_evidence_claim(proc_id, impl_file, test_file, str(e), -1)