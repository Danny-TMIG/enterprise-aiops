"""
Aether Sovereign Fabric — Local Telemetry & Ledger SQLite Store
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any
import json

class TelemetryStore:
    def __init__(self, db_path: str = "storage/swarm_dunbar_m4_max_core_01.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                node_id TEXT,
                metric_data TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_metric(self, node_id: str, data: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO telemetry_logs (node_id, metric_data) VALUES (?, ?)",
            (node_id, json.dumps(data))
        )
        conn.commit()
        conn.close()
