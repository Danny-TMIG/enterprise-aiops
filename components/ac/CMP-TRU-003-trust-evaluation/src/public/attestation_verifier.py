"""
CMP-TRU-003 — Local Hardware & Software Attestation Verifier
Validates node identity, ledger integrity, and Ed25519 cryptographic signatures.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

class AttestationVerifier:
    def __init__(self, public_key_path: str = "storage/node.pub"):
        self.public_key_path = Path(public_key_path)

    def verify_node_receipt(self, receipt_data: Dict[str, Any], signature_hex: str) -> Tuple[bool, str]:
        if not self.public_key_path.exists():
            return False, "Trust anchor public key missing."

        try:
            pub_bytes = bytes.fromhex(self.public_key_path.read_text().strip())
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)

            canonical_payload = json.dumps(receipt_data, sort_keys=True).encode("utf-8")
            sig_bytes = bytes.fromhex(signature_hex)

            public_key.verify(sig_bytes, canonical_payload)
            return True, "Attestation verification passed."
        except InvalidSignature:
            return False, "Cryptographic signature validation failed."
        except Exception as e:
            return False, f"Attestation error: {str(e)}"
