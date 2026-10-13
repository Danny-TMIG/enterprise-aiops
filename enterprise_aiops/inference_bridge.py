import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import aiohttp


class LocalInferenceEngine:
    def __init__(self, endpoint: str = "http://127.0.0.1:8000", model: str = "mlx-community/Qwen2.5-7B-Instruct-4bit"):
        self.endpoint = endpoint
        self.model = model

    async def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.endpoint}/v1/chat/completions", json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"Inference server error [{response.status}]: {text}")
                data = await response.json()
                return data["choices"][0]["message"]["content"]

class InferenceStateBridge:
    def __init__(self, ledger_path: str = "universal_ops_ledger.jsonl"):
        self.engine = LocalInferenceEngine()
        self.ledger_path = Path(ledger_path)

    async def dispatch_and_prove(self, domain: str, prompt: str) -> dict:
        prev_hash = self._get_latest_hash()
        timestamp = datetime.now(timezone.utc).isoformat()
        response = await self.engine.generate(prompt)
        payload = {"domain": domain, "status": "INFERRED", "response": response}
        raw_data = json.dumps({"timestamp": timestamp, "node": domain, "payload": payload, "prev_hash": prev_hash}, sort_keys=True)
        current_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        record = {
            "timestamp": timestamp,
            "node": domain,
            "stage": "AUTO_DISPATCH::INFERENCE",
            "status": "SUCCESS",
            "details": str(payload),
            "prev_hash": prev_hash,
            "current_hash": current_hash
        }
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        return record

    def _get_latest_hash(self) -> str:
        if not self.ledger_path.exists():
            return "0000000000000000000000000000000000000000000000000000000000000000"
        with open(self.ledger_path, "r") as f:
            lines = f.readlines()
            if not lines:
                return "0000000000000000000000000000000000000000000000000000000000000000"
            last_record = json.loads(lines[-1].strip())
            return last_record.get("current_hash", "0000000000000000000000000000000000000000000000000000000000000000")
