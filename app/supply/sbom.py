"""CycloneDX 1.5 SBOM. Real scan, real SHA-256 over every .py."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path


def _h(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

def scan_components(root: Path) -> list[dict]:
    out = []
    for p in sorted(root.rglob("*.py")):
        s = str(p)
        if "/.venv/" in s or "/__pycache__/" in s or "/node_modules/" in s: continue
        raw = p.read_bytes()
        rel = str(p.relative_to(root))
        name = rel[:-3].replace("/", ".") if rel.endswith(".py") else rel
        out.append({"type":"library","name":name,"version":"0.0.0",
                    "hashes":[{"alg":"SHA-256","content":_h(raw)}],
                    "properties":[{"name":"path","value":rel},
                                  {"name":"size","value":str(len(raw))}]})
    return out

def build_sbom(name: str, version: str, root: Path | None = None) -> dict:
    root = root or Path.cwd()
    return {"bomFormat":"CycloneDX","specVersion":"1.5",
            "serialNumber":f"urn:uuid:{uuid.uuid4()}","version":1,
            "metadata":{"timestamp":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "component":{"type":"application","name":name,"version":version}},
            "components":scan_components(root)}

def sbom_digest(sbom: dict) -> str:
    return _h(json.dumps(sbom, sort_keys=True).encode())
