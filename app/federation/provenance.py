import hashlib
import json
from datetime import UTC, datetime
from typing import Any


class ExecutionProvenanceLedger:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.chain: list[Any] = []

    def record_execution(
        self, payload: dict[str, Any], previous_hash: str = "0"
    ) -> dict[str, Any]:
        timestamp = datetime.now(UTC).isoformat()
        serialized_payload = json.dumps(payload, sort_keys=True)
        block_content = (
            f"{previous_hash}:{self.node_id}:{timestamp}:{serialized_payload}"
        )
        signature_hash = hashlib.sha256(block_content.encode("utf-8")).hexdigest()

        block = {
            "node_id": self.node_id,
            "timestamp": timestamp,
            "previous_hash": previous_hash,
            "payload_hash": hashlib.sha256(
                serialized_payload.encode("utf-8")
            ).hexdigest(),
            "signature": signature_hash,
        }
        self.chain.append(block)
        return block
