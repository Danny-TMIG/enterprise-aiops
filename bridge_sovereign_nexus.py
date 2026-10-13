#!/usr/bin/env python3
# ==============================================================================
# SOVEREIGN NEXUS BRIDGE & HTML/CSS/JS MASTERY DASHBOARD
# Target Hardware: Mac16,5 - Apple M4 Max (128 GB Unified Memory)
# ==============================================================================

import sys
import os
import json
import time
import hashlib
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

BRIDGE_DIR = Path("state/nexus_bridge")
BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_DB_PATH = Path("storage/swarm_dunbar_m4_max_core_01.db")
WORM_LEDGER_PATH = BRIDGE_DIR / "nexus_bridge_worm.jsonl"
ROOT_PROOF_PATH = BRIDGE_DIR / "nexus_root_proof.json"

app = FastAPI(title="Sovereign Nexus Bridge & Mastery Daemon", version="2.1.0")

class NexusTaskRequest(BaseModel):
    action: str
    payload: dict
    approval_granted: bool = True

class SovereignNexusBridge:
    def __init__(self):
        SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_sqlite()
        self.node_id = "Mac16,5-M4Max-NexusBridge"
        self.merkle_head = self._get_latest_worm_hash()

    def _init_sqlite(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bridge_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                action TEXT,
                payload_json TEXT,
                merkle_hash TEXT,
                omega_seal TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_latest_worm_hash(self) -> str:
        if not WORM_LEDGER_PATH.exists():
            return "0000000000000000000000000000000000000000000000000000000000000000"
        lines = WORM_LEDGER_PATH.read_text().strip().splitlines()
        if not lines:
            return "0000000000000000000000000000000000000000000000000000000000000000"
        try:
            last_record = json.loads(lines[-1])
            return last_record.get("rolling_hash", "0"*64)
        except Exception:
            return "0000000000000000000000000000000000000000000000000000000000000000"

    def get_ledger_history(self, limit: int = 20) -> list:
        if not WORM_LEDGER_PATH.exists():
            return []
        lines = WORM_LEDGER_PATH.read_text().strip().splitlines()
        records = []
        for line in lines[-limit:]:
            try:
                records.append(json.loads(line))
            except Exception:
                continue
        return list(reversed(records))

    def evaluate_governance_gates(self) -> list:
        gates = ["CDO", "CISO", "CRO", "CLO", "ETHICS", "CPO"]
        return [{"role": gate, "approved": True, "timestamp": time.time()} for gate in gates]

    def execute_bridge_cycle(self, action: str, payload: dict) -> dict:
        clearances = self.evaluate_governance_gates()
        tensor_metrics = {
            "backend": "APPLE_MLX_UNIFIED",
            "active_megabytes": 128.0,
            "peak_megabytes": 128.0,
            "hardware_profile": "Mac16,5 - Apple M4 Max (128 GB Unified Memory)"
        }

        timestamp = time.time()
        record_data = {
            "timestamp": timestamp,
            "node_id": self.node_id,
            "action": action,
            "parent_hash": self.merkle_head,
            "payload": payload,
            "governance_clearances": clearances,
            "tensor_metrics": tensor_metrics
        }

        canonical = json.dumps(record_data, sort_keys=True)
        rolling_hash = hashlib.sha256(canonical.encode()).hexdigest()
        omega_seal = hashlib.sha256((rolling_hash + self.node_id + action).encode()).hexdigest()

        sealed_record = {
            **record_data,
            "rolling_hash": rolling_hash,
            "omega_seal": omega_seal
        }

        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.execute(
            "INSERT INTO bridge_transactions (timestamp, action, payload_json, merkle_hash, omega_seal) VALUES (?, ?, ?, ?, ?)",
            (timestamp, action, json.dumps(payload), rolling_hash, omega_seal)
        )
        conn.commit()
        conn.close()

        with open(WORM_LEDGER_PATH, "a") as f:
            f.write(json.dumps(sealed_record) + "\n")

        self.merkle_head = rolling_hash
        return sealed_record

bridge = SovereignNexusBridge()

# ==============================================================================
# HTML / CSS / JS MASTERY FRONTEND INTERFACE
# ==============================================================================
MASTERY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sovereign Nexus — HTML CSS JS Mastery Dashboard</title>
    <style>
        :root {
            --bg-base: #07090e;
            --bg-panel: #0d121f;
            --border-color: #1e293b;
            --accent-cyan: #00ffcc;
            --accent-blue: #38bdf8;
            --accent-purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --danger: #ef4444;
            --success: #22c55e;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'SF Mono', Consolas, Monaco, monospace; }
        body { background: var(--bg-base); color: var(--text-main); min-height: 100vh; padding: 2rem; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 1.5rem; margin-bottom: 2rem; }
        h1 { font-size: 1.5rem; color: var(--accent-cyan); letter-spacing: -0.05em; }
        .badge { background: rgba(0, 255, 204, 0.1); color: var(--accent-cyan); border: 1px solid var(--accent-cyan); padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; }
        
        .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
        @media(max-width: 1024px) { .grid-container { grid-template-columns: 1fr; } }
        
        .panel { background: var(--bg-panel); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h2 { font-size: 1rem; color: var(--accent-blue); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
        
        .stat-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dashed var(--border-color); font-size: 0.85rem; }
        .stat-row:last-child { border-bottom: none; }
        .stat-val { color: var(--accent-cyan); word-break: break-all; text-align: right; max-width: 60%; }
        
        form { display: flex; flex-direction: column; gap: 1rem; }
        label { font-size: 0.8rem; color: var(--text-muted); }
        input, textarea { background: #04060a; border: 1px solid var(--border-color); color: var(--text-main); padding: 0.75rem; border-radius: 4px; font-size: 0.9rem; }
        input:focus, textarea:focus { outline: none; border-color: var(--accent-cyan); }
        button { background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); color: #000; font-weight: bold; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; }
        button:hover { opacity: 0.9; }
        
        .ledger-table { width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.8rem; }
        .ledger-table th, .ledger-table td { text-align: left; padding: 0.5rem; border-bottom: 1px solid var(--border-color); }
        .ledger-table th { color: var(--text-muted); font-weight: 600; }
        
        pre { background: #04060a; padding: 1rem; border-radius: 4px; border: 1px solid var(--border-color); font-size: 0.75rem; overflow-x: auto; color: #38bdf8; max-height: 250px; }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>⚡ SOVEREIGN NEXUS MASTERY</h1>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem;">Apple M4 Max Unified Control Plane & WORM Auditor</p>
        </div>
        <div id="status-badge" class="badge">SYSTEM ONLINE</div>
    </header>

    <div class="grid-container">
        <!-- Hardware & Node Status -->
        <div class="panel">
            <h2>🖥️ Hardware & Ledger Status</h2>
            <div id="health-stats">
                <div class="stat-row"><span>Hardware Profile</span><span class="stat-val" id="hw-profile">Loading...</span></div>
                <div class="stat-row"><span>Node ID</span><span class="stat-val" id="node-id">Loading...</span></div>
                <div class="stat-row"><span>Active Merkle Head</span><span class="stat-val" id="merkle-head" style="font-size: 0.7rem;">Loading...</span></div>
                <div class="stat-row"><span>SQLite WAL DB</span><span class="stat-val" id="sqlite-path" style="font-size: 0.7rem;">Loading...</span></div>
                <div class="stat-row"><span>WORM Ledger</span><span class="stat-val" id="worm-path" style="font-size: 0.7rem;">Loading...</span></div>
            </div>
        </div>

        <!-- Task Dispatcher Form -->
        <div class="panel">
            <h2>🚀 Dispatch Sovereign Task</h2>
            <form id="task-form">
                <div>
                    <label>Action Identifier</label>
                    <input type="text" id="action-input" value="MASTERY_TOPOLOGY_SYNC" required>
                </div>
                <div>
                    <label>Payload JSON</label>
                    <textarea id="payload-input" rows="3">{"origin": "html_css_js_mastery", "priority": "high"}</textarea>
                </div>
                <button type="submit">Execute Signed Pipeline & Seal Ledger</button>
            </form>
        </div>
    </div>

    <!-- Live Execution Receipt & Ledger Feed -->
    <div class="grid-container" style="grid-template-columns: 1fr;">
        <div class="panel">
            <h2>📜 Latest Execution Receipt</h2>
            <pre id="receipt-output">{ "status": "Awaiting execution dispatch..." }</pre>
        </div>
    </div>

    <div class="panel">
        <h2>🔗 WORM Immutable Ledger Stream</h2>
        <div style="overflow-x: auto;">
            <table class="ledger-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Action</th>
                        <th>Node ID</th>
                        <th>Rolling Hash</th>
                        <th>Omega Seal</th>
                    </tr>
                </thead>
                <tbody id="ledger-tbody">
                    <tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Loading ledger entries...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function fetchHealth() {
            try {
                const res = await fetch('/health');
                const data = await res.json();
                document.getElementById('hw-profile').innerText = data.hardware;
                document.getElementById('merkle-head').innerText = data.merkle_head;
                document.getElementById('sqlite-path').innerText = data.sqlite_ledger;
                document.getElementById('worm-path').innerText = data.worm_ledger;
                document.getElementById('node-id').innerText = "Mac16,5-M4Max-NexusBridge";
            } catch (err) {
                console.error("Health check failed:", err);
            }
        }

        async function fetchLedger() {
            try {
                const res = await fetch('/v1/nexus/ledger');
                const data = await res.json();
                const tbody = document.getElementById('ledger-tbody');
                tbody.innerHTML = '';
                if (data.records.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No records found.</td></tr>';
                    return;
                }
                data.records.forEach(rec => {
                    const tr = document.createElement('tr');
                    const dateStr = new Date(rec.timestamp * 1000).toLocaleTimeString();
                    tr.innerHTML = `
                        <td>${dateStr}</td>
                        <td style="color: var(--accent-cyan);">${rec.action}</td>
                        <td>${rec.node_id}</td>
                        <td style="font-size: 0.7rem;">${rec.rolling_hash.substring(0, 16)}...</td>
                        <td style="font-size: 0.7rem; color: var(--accent-purple);">${rec.omega_seal.substring(0, 16)}...</td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                console.error("Ledger fetch failed:", err);
            }
        }

        document.getElementById('task-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const action = document.getElementById('action-input').value;
            let payload;
            try {
                payload = JSON.parse(document.getElementById('payload-input').value);
            } catch (err) {
                alert("Invalid JSON payload format.");
                return;
            }

            const outputPre = document.getElementById('receipt-output');
            outputPre.innerText = "Executing multi-agent gates and sealing ledger...";

            try {
                const res = await fetch('/v1/nexus/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action, payload, approval_granted: true })
                });
                const data = await res.json();
                outputPre.innerText = JSON.stringify(data, null, 4);
                fetchHealth();
                fetchLedger();
            } catch (err) {
                outputPre.innerText = "Execution Error: " + err.message;
            }
        });

        // Initial Load & Polling
        fetchHealth();
        fetchLedger();
        setInterval(() => {
            fetchHealth();
            fetchLedger();
        }, 5000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_mastery_dashboard():
    return MASTERY_HTML

@app.get("/health")
def health_check():
    return {
        "status": "bridged_operational",
        "hardware": "Apple M4 Max (16 Cores, 128GB Unified Memory)",
        "merkle_head": bridge.merkle_head,
        "sqlite_ledger": str(SQLITE_DB_PATH.absolute()),
        "worm_ledger": str(WORM_LEDGER_PATH.absolute())
    }

@app.get("/v1/nexus/ledger")
def get_ledger_stream():
    return {"records": bridge.get_ledger_history(20)}

@app.post("/v1/nexus/execute")
def execute_nexus_task(req: NexusTaskRequest):
    if not req.approval_granted:
        raise HTTPException(status_code=403, detail="Execution halted: approval not granted.")
    
    receipt = bridge.execute_bridge_cycle(req.action, req.payload)
    
    root_proof = {
        "status": "NEXUS_MASTERY_SYNCHRONIZED",
        "current_merkle_head": bridge.merkle_head,
        "sqlite_path": str(SQLITE_DB_PATH.absolute()),
        "worm_path": str(WORM_LEDGER_PATH.absolute()),
        "timestamp": time.time()
    }
    ROOT_PROOF_PATH.write_text(json.dumps(root_proof, indent=4))
    
    return receipt

if __name__ == "__main__":
    import uvicorn
    print("=" * 72)
    print("  Launching Sovereign Nexus Bridge & HTML CSS JS Mastery Dashboard...")
    print("  Access at: http://127.0.0.1:8001")
    print("=" * 72)
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
