"""Append-only evidence ledger for the sovereign node."""
from __future__ import annotations

import hashlib
import json
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
