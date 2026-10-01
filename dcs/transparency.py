"""Append-only Merkle-chained log of conformance runs."""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def append(log_path: Path, bundle_digest: str, verdict: str) -> dict:
    """Append one entry, chaining to the previous entry's hash."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    prev = "genesis"
    if log_path.exists():
        last = log_path.read_text().strip().splitlines()
        if last:
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
    return entry


def verify_chain(log_path: Path) -> dict:
    if not log_path.exists():
        return {"entries": 0, "valid": True}
    prev = "genesis"
    n = 0
    for line in log_path.read_text().splitlines():
        e = json.loads(line)
        if e["prev"] != prev:
            return {"entries": n, "valid": False, "broken_at": n}
        h = _hash(json.dumps({k: v for k, v in e.items() if k != "entry_hash"},
                              sort_keys=True))
        if h != e["entry_hash"]:
            return {"entries": n, "valid": False, "broken_at": n, "reason": "hash"}
        prev = e["entry_hash"]
        n += 1
    return {"entries": n, "valid": True}
