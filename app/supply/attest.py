"""in-toto Statement v1 attestation."""
from __future__ import annotations

import json
import time

from app.supply.sign import key_id, sign, verify


def _canon(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True).encode()

def build_attestation(sbom: dict, key: bytes) -> dict:
    subject = [{"name": c["name"], "digest": {"sha256": c["hashes"][0]["content"]}}
               for c in sbom["components"]]
    predicate = {"builder":{"id":"app.supply"},
                 "buildType":"https://enterprise_aiops/build/v1",
                 "metadata":{"serial":sbom["serialNumber"],
                             "specVersion":sbom["specVersion"]},
                 "timestamp":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    stmt = {"_type":"https://in-toto.io/Statement/v1",
            "subject":subject,
            "predicateType":"https://slsa.dev/provenance/v1",
            "predicate":predicate}
    stmt["signature"] = sign(_canon(stmt), key)
    stmt["key_id"] = key_id(key)
    return stmt

def verify_attestation(stmt: dict, key: bytes) -> bool:
    st = dict(stmt)
    sig = st.pop("signature", None)
    kid = st.pop("key_id", None)
    if sig is None or kid != key_id(key): return False
    return verify(_canon(st), sig, key)
