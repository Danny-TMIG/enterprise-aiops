"""Backup / restore round-trip."""
import hashlib
from dcs.generate import requirement

def snapshot(data: bytes) -> dict:
    return {"bytes": data, "sha256": hashlib.sha256(data).hexdigest()}

def restore(snap: dict) -> bytes:
    assert hashlib.sha256(snap["bytes"]).hexdigest() == snap["sha256"]
    return snap["bytes"]

@requirement(id="DCS-XC-BACKUP-001", title="snapshot/restore is integrity-checked",
             section="X.backup", hats=["STE", "SRE", "SD"], criticality="MUST")
def test():
    blob = b"critical" * 1000
    s = snapshot(blob)
    assert restore(s) == blob
    s["bytes"] = b"tampered" + s["bytes"]
    try: restore(s)
    except AssertionError: return
    raise AssertionError("tampered snapshot accepted")
