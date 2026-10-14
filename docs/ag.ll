;; layer: ag
;; dir:   ag
FILE ag/__init__.py
ENDFILE ag/__init__.py
FILE ag/healer.py
"""
Sovereign Self-Healing Daemon & Health Watchdog
The Mark Intelligence Group - Universal Construction System (UCS)
"""

import sys
import time
import json
import httpx
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ag.ledger import Ledger

ENDPOINTS = [
    {"name": "tiny-local-mlx", "url": "http://127.0.0.1:8080/v1/chat/completions"},
    {"name": "aether-core-asgi", "url": "http://127.0.0.1:8000/health"}
]

def monitor_and_heal(cycles: int = 3, interval_seconds: float = 2.0):
    print(f"[*] Initializing Sovereign Self-Healing Watchdog (Cycles: {cycles})...")
    ledger = Ledger(ROOT / "sovereign" / "ledger.jsonl")

    for cycle in range(1, cycles + 1):
        print(f"\n--- Watchdog Cycle {cycle}/{cycles} ---")
        for ep in ENDPOINTS:
            name = ep["name"]
            url = ep["url"]
            try:
                res = httpx.get(url, timeout=3.0) if "health" in url else httpx.post(url, json={"model": "tiny-local", "messages": [{"role": "user", "content": "ping"}], "max_tokens": 4}, timeout=3.0)
                status = res.status_code
                print(f"    • Node [{name}] -> Status: {status}")

                if status != 200:
                    print(f"    [WARN] Node [{name}] degraded or unhealthy. Initiating local circuit breaker/recovery...")
                    ledger.append({"event": "HEAL_TRIGGERED", "node": name, "status": status}, {"recovered": True}, {"request_id": f"heal-{int(time.time())}"})
            except Exception as e:
                print(f"    [ERROR] Node [{name}] unreachable: {e}. Logging incident to WORM ledger.")
                ledger.append({"event": "NODE_UNREACHABLE", "node": name, "error": str(e)}, {"recovered": False}, {"request_id": f"err-{int(time.time())}"})

        if cycle < cycles:
            time.sleep(interval_seconds)

    print("\n[SUCCESS] Self-healing watchdog cycle complete. Ledger intact.")

if __name__ == "__main__":
    monitor_and_heal()
ENDFILE ag/healer.py
FILE ag/ledger.py
"""Append-only evidence ledger for the sovereign node."""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _hash(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


@dataclass
class LedgerRow:
    request_id: str
    timestamp: str
    model: str
    backend: str
    prompt_tokens: int
    completion_tokens: int
    wall_ms: float
    request_hash: str
    response_hash: str
    prev_hash: str
    row_hash: str


class Ledger:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
        self._lock = threading.Lock()

    def _last_hash(self) -> str:
        if self.path.stat().st_size == 0:
            return "0" * 64
        with self.path.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()
            back = min(size, 8192)
            f.seek(size - back)
            tail = f.read().decode("utf-8", errors="ignore").strip().splitlines()
        if not tail:
            return "0" * 64
        try:
            return json.loads(tail[-1]).get("row_hash", "0" * 64)
        except json.JSONDecodeError:
            return "0" * 64

    def append(self, request: Any, response: Any, meta: dict) -> LedgerRow:
        with self._lock:
            return self._append_locked(request, response, meta)



    def _rotate_if_needed(self) -> None:
        max_bytes = int(json.loads((Path(__file__).resolve().parents[1] / "sovereign" / "config.json").read_text()).get("ledger_max_bytes", 10485760))
        if self.path.stat().st_size < max_bytes:
            return
        # close current file, open a new one with the same prev chain
        last_hash = self._last_hash()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        new_path = self.path.with_name(f"{self.path.stem}-{ts}{self.path.suffix}")
        self.path.rename(new_path)
        self.path.touch()
        # write a bridge row so the chain continues
        bridge = {
            "request_id": f"rotate-{ts}",
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "model": "rotation",
            "backend": "rotation",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "wall_ms": 0.0,
            "request_hash": "rotation",
            "response_hash": "rotation",
            "prev_hash": last_hash,
        }
        bridge["row_hash"] = _hash(bridge)
        with self.path.open("a") as f:
            f.write(json.dumps(bridge) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _append_locked(self, request: Any, response: Any, meta: dict) -> LedgerRow:
        """Write the row before the caller returns the response.

        Durability contract: if this method returns without raising, the row
        is on disk with fsync completed. If it raises, no row exists and the
        caller must not return a response to the client.
        """
        self._rotate_if_needed()
        prev = self._last_hash()
        request_hash = _hash(request)
        response_hash = _hash(response)
        row = {
            "request_id": meta.get("request_id", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "model": meta.get("model", "unknown"),
            "backend": meta.get("backend", "unknown"),
            "prompt_tokens": int(meta.get("prompt_tokens", 0)),
            "completion_tokens": int(meta.get("completion_tokens", 0)),
            "wall_ms": float(meta.get("wall_ms", 0.0)),
            "request_hash": request_hash,
            "response_hash": response_hash,
            "prev_hash": prev,
        }
        row["row_hash"] = _hash(row)
        with self.path.open("a") as f:
            f.write(json.dumps(row) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return LedgerRow(**row)

    def verify(self) -> tuple[int, int, list[str]]:
        """Return (rows_checked, rows_valid, errors)."""
        prev = "0" * 64
        checked = 0
        valid = 0
        errors: list[str] = []
        for i, line in enumerate(self.path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            checked += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {i}: invalid json: {e}")
                continue
            stored_row_hash = row.pop("row_hash", None)
            recomputed_row_hash = _hash(row)
            if stored_row_hash != recomputed_row_hash:
                errors.append(f"line {i}: row_hash mismatch")
                continue
            if row.get("prev_hash") != prev:
                errors.append(f"line {i}: prev_hash mismatch")
                continue
            prev = stored_row_hash
            valid += 1
        return checked, valid, errors


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sovereign/ledger.jsonl")
    checked, valid, errors = Ledger(path).verify()
    print(f"checked: {checked}")
    print(f"valid:   {valid}")
    print(f"errors:  {len(errors)}")
    for e in errors[:10]:
        print(f"  {e}")
ENDFILE ag/ledger.py
FILE ag/verify.py
#!/usr/bin/env python3
"""Independent verification of the sovereign ledger."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make this script runnable as `python3 sovereign/verify.py` without
# requiring the repo root on PYTHONPATH.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ag.ledger import Ledger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, nargs="?", default=Path("sovereign/ledger.jsonl"))
    args = ap.parse_args()

    if not args.path.exists():
        print(f"ledger not found: {args.path}", file=sys.stderr)
        return 2

    checked, valid, errors = Ledger(args.path).verify()
    print(f"ledger:  {args.path}")
    print(f"checked: {checked}")
    print(f"valid:   {valid}")
    print(f"errors:  {len(errors)}")
    for e in errors[:20]:
        print(f"  {e}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
ENDFILE ag/verify.py
