"""
Sovereign Cryptographic Utilities (Ed25519 & SHA-256 Omega Sealing)
"""
import hashlib
import json

def compute_omega_seal(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()

def verify_signature(payload: dict, public_key: str, signature: str) -> bool:
    # Placeholder for Ed25519 verification logic
    expected_hash = compute_omega_seal(payload)
    return len(signature) > 0 and len(public_key) > 0
