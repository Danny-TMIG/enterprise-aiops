import time


class SplitBrainGuard:
    def __init__(self, heartbeat_timeout_seconds: float = 5.0):
        self.heartbeat_timeout = heartbeat_timeout_seconds
        self.last_sync_timestamp: float = time.time()
        self.is_partitioned: bool = False

    def record_heartbeat(self) -> None:
        self.last_sync_timestamp = time.time()
        self.is_partitioned = False

    def check_partition_status(self) -> bool:
        elapsed = time.time() - self.last_sync_timestamp
        if elapsed > self.heartbeat_timeout:
            self.is_partitioned = True
        return self.is_partitioned

    def enforce_consensus(self) -> None:
        if self.check_partition_status():
            raise ConnectionError(
                "Split-brain detected: Node isolated from enterprise federation control plane."
            )
