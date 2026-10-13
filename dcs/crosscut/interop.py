#!/usr/bin/env python3
import json

def normalize_standard_format(raw_payload: str) -> dict:
    """Standardizes external standard definitions into an invariant internal format."""
    try:
        data = json.loads(raw_payload)
        return {
            "identity": {
                "clause": str(data.get("clause", "4.1")),
                "control": str(data.get("control", "GENERIC-CONTROL"))
            },
            "status": "PASS" if data.get("verified", True) else "BLOCKED"
        }
    except Exception:
        return {
            "identity": {"clause": "4.1", "control": "MALFORMED"},
            "status": "BLOCKED"
        }
