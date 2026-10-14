import json
from pathlib import Path

def merge_compliance_telemetry(base: dict, operational: dict) -> dict:
    """Coalesces distinct operational telemetry sets into a unified verification ledger."""
    coalesced = base.copy()
    for key, value in operational.items():
        if key in coalesced and isinstance(coalesced[key], dict) and isinstance(value, dict):
            coalesced[key].update(value)
        else:
            coalesced[key] = value
    return coalesced
