import mmap
import os
import struct
import hashlib
import time
import logging
from typing import Generator, Dict, Any

logging.basicConfig(level=logging.INFO, format="[+] %(asctime)s [%(levelname)s] %(message)s")

class RollingPrimeSubstrateEngine:
    """
    Eliminates static allocations by using prime-dimensioned ring buffers,
    floating-point temporal decay weights, and dynamic rolling primitives.
    """
    def __init__(self, path: str = "enterprise_aiops/prime_state.mmap", prime_capacity: int = 1031):
        self.path = path
        self.prime_capacity = prime_capacity
        self.header_size = 64
        self.slot_footprint = 1 + 32 + 8 + 8  # Active Flag (1B) | State Hash (32B) | Weight (8B) | Timestamp (8B)
        self.total_size = self.header_size + (self.prime_capacity * self.slot_footprint)
        self._initialize_substrate()

    def _initialize_substrate(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        file_exists = os.path.exists(self.path)
        with open(self.path, "r+b" if file_exists else "w+b") as f:
            if not file_exists:
                f.write(b'\x00' * self.total_size)
            f.flush()

    def _prime_modulo_address(self, key_hash: bytes) -> int:
        int_val = int.from_bytes(key_hash[:8], byteorder='big')
        return int_val % self.prime_capacity

    def commit_rolling_state(self, state_hash: str, floating_weight: float) -> Dict[str, Any]:
        hash_bytes = bytes.fromhex(state_hash)
        slot_index = self._prime_modulo_address(hash_bytes)
        offset = self.header_size + (slot_index * self.slot_footprint)
        timestamp = time.time()
        
        packed_data = struct.pack('=B 32s d d', 0x01, hash_bytes, floating_weight, timestamp)
        
        with open(self.path, "r+b") as f:
            with mmap.mmap(f.fileno(), self.total_size) as mm:
                mm[offset:offset + len(packed_data)] = packed_data
                mm.flush()
                
        block_signature = hashlib.sha256(packed_data).hexdigest()
        logging.info(f"Committed rolling state to prime slot {slot_index} (Weight: {floating_weight:.6f})")
        
        return {
            "prime_slot": slot_index,
            "block_signature": block_signature,
            "timestamp": timestamp,
            "floating_weight": floating_weight
        }

    def stream_rolling_window(self, window_size: int = 17) -> Generator[Dict[str, Any], None, None]:
        with open(self.path, "r+b") as f:
            with mmap.mmap(f.fileno(), self.total_size) as mm:
                for i in range(window_size):
                    slot_index = (i * 101) % self.prime_capacity
                    offset = self.header_size + (slot_index * self.slot_footprint)
                    slot_data = mm[offset:offset + self.slot_footprint]
                    
                    if slot_data[0] == 0x01:
                        _, h_bytes, weight, ts = struct.unpack('=B 32s d d', slot_data)
                        yield {
                            "slot_id": slot_index,
                            "state_hash": h_bytes.hex(),
                            "floating_weight": weight,
                            "timestamp": ts
                        }
