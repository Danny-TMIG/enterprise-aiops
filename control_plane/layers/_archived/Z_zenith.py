"""Z — Zenith. Role: Close."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from control_plane.layer_base import LayerBase


@dataclass
class ZenithLayer(LayerBase):
    letter: str = "Z"
    name: str = "Zenith"
    role: str = "Close"
    reads: tuple[str, ...] = ("ALL",)
    writes: tuple[str, ...] = ("ZenithSeal",)
    pollinates: tuple[str, ...] = ()
    artifact: str = "zenith-seal"

    def _produce(self, inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        # refuse to seal if any layer status is not PASS
        letters = sorted(k for k in context.keys() if len(k) == 1 and k.isalpha())
        for letter in letters:
            payload = context[letter]
            if isinstance(payload, dict) and payload.get("_status") and payload["_status"] != "PASS":
                return {
                    "artifact": self.artifact,
                    "produced_by": f"{self.letter}.{self.name}",
                    "reads": ["ALL"],
                    "summary": f"Cannot seal: {letter} status is {payload['_status']}.",
                    "run_id": str(context.get("correlation_id", "unset")),
                    "artifact_hashes": [],
                    "merkle_root": "",
                    "signature": "",
                }
        hashes = []
        for letter in letters:
            payload_json = json.dumps(context[letter], sort_keys=True, default=str)
            hashes.append({"letter": letter, "hash": hashlib.sha256(payload_json.encode()).hexdigest()})
        leaves = [h["hash"] for h in hashes]
        if leaves:
            while len(leaves) > 1:
                if len(leaves) % 2:
                    leaves.append(leaves[-1])
                leaves = [hashlib.sha256((leaves[i] + leaves[i + 1]).encode()).hexdigest() for i in range(0, len(leaves), 2)]
            root = leaves[0]
        else:
            root = ""
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        sig = hashlib.sha256(f"{root}{ts}".encode()).hexdigest()
        return {
            "artifact": self.artifact,
            "produced_by": f"{self.letter}.{self.name}",
            "reads": ["ALL"],
            "summary": f"Seal over {len(hashes)} artifacts, root {root[:16]}.",
            "run_id": str(context.get("correlation_id", "unset")),
            "artifact_hashes": hashes,
            "merkle_root": root,
            "signature": sig,
        }
