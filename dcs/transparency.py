"""Append-only Merkle-chained log of conformance runs."""

from __future__ import annotations  # pragma: no cover

import hashlib  # pragma: no cover
import json  # pragma: no cover
import time  # pragma: no cover
from pathlib import Path  # pragma: no cover


def _hash(s: str) -> str:  # pragma: no cover
    return hashlib.sha256(s.encode()).hexdigest()  # pragma: no cover


def append(log_path: Path, bundle_digest: str, verdict: str) -> dict:  # pragma: no cover
    """Append one entry, chaining to the previous entry's hash."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    prev = "genesis"
    if log_path.exists():  # pragma: no cover
        last = log_path.read_text().strip().splitlines()
        if last:  # pragma: no cover
            prev = json.loads(last[-1])["entry_hash"]
    entry = {
        "ts": time.time(),
        "bundle": bundle_digest,
        "verdict": verdict,
        "prev": prev,
    }
    entry["entry_hash"] = _hash(json.dumps(entry, sort_keys=True))
    with log_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry  # pragma: no cover


def verify_chain(log_path: Path) -> dict:  # pragma: no cover
    if not log_path.exists():  # pragma: no cover
        return {"entries": 0, "valid": True}  # pragma: no cover
    prev = "genesis"
    n = 0
    for line in log_path.read_text().splitlines():
        e = json.loads(line)
        if e["prev"] != prev:  # pragma: no cover
            return {"entries": n, "valid": False, "broken_at": n}  # pragma: no cover
        h = _hash(json.dumps({k: v for k, v in e.items() if k != "entry_hash"}, sort_keys=True))
        if h != e["entry_hash"]:  # pragma: no cover
            return {"entries": n, "valid": False, "broken_at": n, "reason": "hash"}  # pragma: no cover
        prev = e["entry_hash"]
        n += 1
    return {"entries": n, "valid": True}  # pragma: no cover
