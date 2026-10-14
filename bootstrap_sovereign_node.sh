#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"

mkdir -p sovereign

# ============================================================== 1. CONFIG
python3 - <<'PYEOF'
from pathlib import Path
import json

Path("sovereign/config.json").write_text(json.dumps({
  "schema_version": "1.0",
  "node_id": "sovereign-01",
  "host": "127.0.0.1",
  "port": 8080,
  "backend": "torch-mps",
  "model": "tiny-local",
  "model_path": "models/tiny",
  "max_concurrency": 1,
  "ledger_path": "sovereign/ledger.jsonl",
  "hardware": {
    "chip": "Apple M4 Max",
    "cores": 16,
    "memory_gb": 128
  },
  "backends": {
    "torch-mps": {"device": "mps", "dtype": "float32"},
    "torch-cpu": {"device": "cpu", "dtype": "float32"},
    "mlx": {"dtype": "float16"}
  }
}, indent=2))
print("wrote sovereign/config.json")
PYEOF

# ============================================================== 2. LEDGER
cat > sovereign/ledger.py <<'PY'
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
PY
chmod +x sovereign/ledger.py

# ============================================================== 3. VERIFIER (CLI)
cat > sovereign/verify.py <<'PY'
#!/usr/bin/env python3
"""Independent verification of the sovereign ledger."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from sovereign.ledger import Ledger


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
PY
chmod +x sovereign/verify.py

# ============================================================== 4. NODE (FastAPI)
cat > sovereign/node.py <<'PY'
#!/usr/bin/env python3
"""Sovereign node — OpenAI-compatible local inference server with evidence ledger.

Runs on one machine. No cloud. Every request is written to a
tamper-evident ledger before the response is returned.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from sovereign.ledger import Ledger


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "sovereign" / "config.json").read_text())
LEDGER = Ledger(ROOT / CONFIG["ledger_path"])

app = FastAPI(title="Sovereign Node", version="1.0")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "tiny-local"
    messages: list[Message]
    max_tokens: int = 128
    temperature: float = 0.0


def _count_tokens(text: str) -> int:
    # Rough estimate: 1 token ~ 4 characters. Real backends use a tokenizer.
    return max(1, len(text) // 4)


def _generate(request: ChatRequest) -> tuple[str, int, int]:
    """Deterministic placeholder that proves the pipeline.

    Replace with a real backend call (mlx_lm or transformers) when a model
    is available at config["model_path"]. The pipeline — ledger, wire format,
    hashing — is identical either way.
    """
    prompt_text = " ".join(m.content for m in request.messages)
    prompt_tokens = _count_tokens(prompt_text)
    # Echo-style response so the pipeline is observable end to end.
    response = f"[sovereign] received {len(request.messages)} message(s) for model {request.model}"
    completion_tokens = _count_tokens(response)
    return response, prompt_tokens, completion_tokens


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "node_id": CONFIG["node_id"],
        "backend": CONFIG["backend"],
        "model": CONFIG["model"],
    }


@app.post("/v1/chat/completions")
def chat(req: ChatRequest) -> dict[str, Any]:
    t0 = time.time()
    request_id = f"chatcmpl-{uuid.uuid4()}"
    try:
        content, prompt_tokens, completion_tokens = _generate(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    wall_ms = (time.time() - t0) * 1000.0
    response_body = {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0,
            },
        },
        "choices": [{
            "message": {"role": "assistant", "content": content},
            "logprobs": None,
            "finish_reason": "stop",
            "index": 0,
        }],
    }

    LEDGER.append(
        request=req.model_dump(),
        response=response_body,
        meta={
            "request_id": request_id,
            "model": req.model,
            "backend": CONFIG["backend"],
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "wall_ms": wall_ms,
        },
    )

    return response_body


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "sovereign.node:app",
        host=CONFIG["host"],
        port=CONFIG["port"],
        reload=False,
    )
PY
chmod +x sovereign/node.py

# ============================================================== 5. SMOKE TEST
cat > tests/test_sovereign_node.py <<'PY'
"""End-to-end test of the sovereign node pipeline."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from sovereign.ledger import Ledger


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Redirect the ledger to a temp file for this test
    import sovereign.node as node_mod
    from pathlib import Path as P
    test_ledger = Ledger(tmp_path / "ledger.jsonl")
    monkeypatch.setattr(node_mod, "LEDGER", test_ledger)
    return TestClient(node_mod.app), test_ledger


def test_health(client):
    c, _ = client
    r = c.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "node_id" in body


def test_chat_completion_wire_format(client):
    c, _ = client
    r = c.post("/v1/chat/completions", json={
        "model": "tiny-local",
        "messages": [{"role": "user", "content": "hello"}],
    })
    assert r.status_code == 200
    body = r.json()
    for key in ("id", "object", "created", "model", "usage", "choices"):
        assert key in body
    assert body["object"] == "chat.completion"
    for key in ("prompt_tokens", "completion_tokens", "total_tokens",
                "completion_tokens_details"):
        assert key in body["usage"]
    assert body["choices"][0]["message"]["role"] == "assistant"
    assert body["choices"][0]["finish_reason"] == "stop"


def test_ledger_records_request(client):
    c, ledger = client
    c.post("/v1/chat/completions", json={
        "model": "tiny-local",
        "messages": [{"role": "user", "content": "one"}],
    })
    c.post("/v1/chat/completions", json={
        "model": "tiny-local",
        "messages": [{"role": "user", "content": "two"}],
    })
    assert ledger.path.exists()
    lines = ledger.path.read_text().strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert second["prev_hash"] == first["row_hash"]


def test_ledger_verifies(client):
    c, ledger = client
    for i in range(3):
        c.post("/v1/chat/completions", json={
            "model": "tiny-local",
            "messages": [{"role": "user", "content": f"msg {i}"}],
        })
    checked, valid, errors = ledger.verify()
    assert checked == 3
    assert valid == 3
    assert errors == []


def test_ledger_detects_tamper(client):
    c, ledger = client
    c.post("/v1/chat/completions", json={
        "model": "tiny-local",
        "messages": [{"role": "user", "content": "a"}],
    })
    c.post("/v1/chat/completions", json={
        "model": "tiny-local",
        "messages": [{"role": "user", "content": "b"}],
    })
    # Tamper with the first row
    lines = ledger.path.read_text().splitlines()
    row = json.loads(lines[0])
    row["completion_tokens"] = 99999
    lines[0] = json.dumps(row)
    ledger.path.write_text("\n".join(lines) + "\n")
    checked, valid, errors = ledger.verify()
    assert checked == 2
    assert valid == 1
    assert any("row_hash mismatch" in e for e in errors)
PY
echo "wrote tests/test_sovereign_node.py"

echo
echo "=== install test deps ==="
pip install --quiet fastapi httpx pytest 2>/dev/null || pip install fastapi httpx pytest
echo "deps ok"

echo
echo "=== run sovereign tests ==="
python -m pytest tests/test_sovereign_node.py -q 2>&1 | tail -15

echo
echo "=== full suite ==="
python -m pytest -q 2>&1 | tail -5
