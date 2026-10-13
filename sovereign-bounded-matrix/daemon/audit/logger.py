import hmac
import hashlib
import json
import time

class ChainedAuditLogger:
    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.previous_hash = "0" * 64

    def log_event(self, event_type: str, actor: str, payload: dict) -> dict:
        entry = {
            "timestamp": time.time(),
            "actor": actor,
            "event_type": event_type,
            "payload": payload,
            "previous_hash": self.previous_hash
        }
        entry_str = json.dumps(entry, sort_keys=True)
        current_hash = hmac.new(self.secret_key, entry_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        signed_entry = {**entry, "current_hash": current_hash}
        self.previous_hash = current_hash
        return signed_entry
