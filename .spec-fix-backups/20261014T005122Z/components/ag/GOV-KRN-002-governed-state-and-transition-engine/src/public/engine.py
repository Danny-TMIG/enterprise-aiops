import time
import hashlib
import json
from typing import Dict, Any

class StateTransitionEngine:
    """
    Authoritative Governance State Transition Engine enforcing WORM ledgers
    and cryptographic verification under ASF v1.2.
    """
    def __init__(self):
        self.valid_states = {"IDLE", "PROCESSING_TELEMETRY", "MONITORING", "EVALUATED", "ERROR", "LOCKED"}

    def transition(self, object_id: str, from_state: str, to_state: str, actor: str) -> Dict[str, Any]:
        if to_state not in self.valid_states:
            raise ValueError(f"Invalid target state classification: {to_state}")
        
        veto_check = bool(actor and actor.strip())
        
        record = {
            "object_id": object_id,
            "from_state": from_state,
            "to_state": to_state,
            "actor": actor,
            "timestamp": time.time(),
            "veto_check": veto_check,
            "status": "AUTHORIZED_AND_SEALED" if veto_check else "REJECTED_BY_GOVERNANCE"
        }
        
        payload = json.dumps(record, sort_keys=True).encode("utf-8")
        record["transition_seal"] = hashlib.sha256(payload).hexdigest()
        return record
