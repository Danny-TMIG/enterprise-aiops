#!/usr/bin/env python3
import json
from pathlib import Path

SCHEMAS = {
    "contracts/gov/object_model_v1.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "GovernanceObjectModel",
        "type": "object",
        "required": ["object_id", "layer", "owner", "created_at", "schema_version"],
        "properties": {
            "object_id": {"type": "string", "pattern": "^GOV-[A-Z]+-[0-9]+$"},
            "layer": {"type": "string", "enum": ["AG", "AX", "AC"]},
            "owner": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "schema_version": {"type": "string", "default": "1.0.0"},
            "metadata": {"type": "object"},
            "signature": {
                "type": "object",
                "required": ["algorithm", "public_key", "value"],
                "properties": {
                    "algorithm": {"type": "string", "enum": ["Ed25519"]},
                    "public_key": {"type": "string"},
                    "value": {"type": "string"}
                }
            }
        }
    },
    "contracts/gov/transition_v1.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "GovernedStateTransition",
        "type": "object",
        "required": ["transition_id", "object_id", "from_state", "to_state", "actor", "timestamp"],
        "properties": {
            "transition_id": {"type": "string", "format": "uuid"},
            "object_id": {"type": "string"},
            "from_state": {"type": "string"},
            "to_state": {"type": "string"},
            "actor": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
            "evidence_ref": {"type": "string"},
            "veto_check": {
                "type": "boolean",
                "description": "Indicates whether C-suite active veto circuit breakers cleared."
            }
        }
    },
    "contracts/ac/telemetry_v1.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "ObservationTelemetryEvent",
        "type": "object",
        "required": ["event_id", "timestamp", "node_id", "metrics"],
        "properties": {
            "event_id": {"type": "string", "format": "uuid"},
            "timestamp": {"type": "string", "format": "date-time"},
            "node_id": {"type": "string"},
            "metrics": {
                "type": "object",
                "required": ["cpu_load_percent", "ram_used_bytes", "ram_total_bytes"],
                "properties": {
                    "cpu_load_percent": {"type": "number", "minimum": 0.0, "maximum": 100.0},
                    "ram_used_bytes": {"type": "integer"},
                    "ram_total_bytes": {"type": "integer"},
                    "mlx_vram_active_bytes": {"type": "integer"}
                }
            },
            "provenance_hash": {"type": "string", "description": "SHA-256 omega seal."}
        }
    }
}

def main():
    print("📜 [CONTRACTS] Generating canonical JSON schemas...")
    for filepath, schema in SCHEMAS.items():
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(schema, indent=2) + "\n")
        print(f"  ✔ Created {filepath}")
    print("💯 [COMPLETE] Canonical schemas successfully compiled.")

if __name__ == "__main__":
    main()
