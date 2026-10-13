#!/usr/bin/env bash
set -e

echo "=================================================="
echo "  Omni-NCF Fabric: Sovereign Bootstrap & Scaffold"
echo "=================================================="

# 1. Ensure directory structure exists
echo "[*] Creating required directories..."
mkdir -p vatican/proof

# 2. Write TLA+ Formal Specification
echo "[*] Writing TLA+ specification to vatican/proof/omni_ncf.tla..."
cat << 'TLA_EOF' > vatican/proof/omni_ncf.tla
---------------------------- MODULE omni_ncf ----------------------------
EXTENDS Integers, Sequences, FiniteSets

CONSTANTS Nodes, MaxEpoch

VARIABLES state, locked, verified_corpus, epoch

vars == <<state, locked, verified_corpus, epoch>>

Init == 
    /\ state = "Idle"
    /\ locked = FALSE
    /\ verified_corpus = FALSE
    /\ epoch = 0

AcquireLock ==
    /\ state = "Idle"
    /\ ~locked
    /\ locked' = TRUE
    /\ state' = "Locked"
    /\ UNCHANGED <<verified_corpus, epoch>>

VerifyCorpus ==
    /\ state = "Locked"
    /\ ~verified_corpus
    /\ verified_corpus' = TRUE
    /\ state' = "Verified"
    /\ UNCHANGED <<locked, epoch>>

SyncConsensus ==
    /\ state = "Verified"
    /\ epoch < MaxEpoch
    /\ epoch' = epoch + 1
    /\ locked' = FALSE
    /\ verified_corpus' = FALSE
    /\ state' = "Idle"

Next == 
    \/ AcquireLock
    \/ VerifyCorpus
    \/ SyncConsensus

Spec == Init /\ [][Next]_vars

* Invariants
SafetyInvariant == (state = "Verified") => locked
EpochBound == epoch <= MaxEpoch

=============================================================================
TLA_EOF

# 3. Write P2P Gossip Protocol Module
echo "[*] Writing P2P gossip module to p2p_gossip.py..."
cat << 'PY_EOF' > p2p_gossip.py
import asyncio
import json
import logging
import socket
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OmniNCF-Gossip")

class P2PGossipNode:
    def __init__(self, host: str = "0.0.0.0", port: int = 9000, peer_ports: list = None):
        self.host = host
        self.port = port
        self.peer_ports = peer_ports or []
        self.state: Dict[str, Any] = {
            "status": "active",
            "model": "mlx-community/Qwen2.5-7B-Instruct-4bit",
            "epoch": 0
        }

    async def handle_peer(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(4096)
        if data:
            try:
                incoming_state = json.loads(data.decode("utf-8"))
                logger.info(f"Received sync state from peer: {incoming_state}")
                if incoming_state.get("epoch", 0) > self.state["epoch"]:
                    self.state["epoch"] = incoming_state["epoch"]
                    logger.info(f"Updated local epoch to {self.state['epoch']}")
            except Exception as e:
                logger.error(f"Failed to parse peer state payload: {e}")
        
        response = json.dumps(self.state).encode("utf-8")
        writer.write(response)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def start_server(self):
        server = await asyncio.start_server(self.handle_peer, self.host, self.port)
        logger.info(f"P2P Gossip listener active on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def broadcast_state(self):
        while True:
            await asyncio.sleep(10)
            self.state["epoch"] += 1
            for p_port in self.peer_ports:
                if p_port == self.port:
                    continue
                try:
                    reader, writer = await asyncio.open_connection("127.0.0.1", p_port)
                    writer.write(json.dumps(self.state).encode("utf-8"))
                    await writer.drain()
                    
                    data = await reader.read(4096)
                    writer.close()
                    await writer.wait_closed()
                    logger.info(f"Successfully gossiped with peer on port {p_port}")
                except Exception:
                    logger.debug(f"Peer on port {p_port} unreachable.")

    async def run(self):
        await asyncio.gather(
            self.start_server(),
            self.broadcast_state()
        )

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    peers = [9000, 9001, 9002]
    node = P2PGossipNode(port=port, peer_ports=peers)
    try:
        asyncio.run(node.run())
    except KeyboardInterrupt:
        logger.info("Gossip node shutdown initiated.")
PY_EOF

# 4. Set Permissions & Validate Artifacts
chmod +x p2p_gossip.py
echo "[*] Validating generated artifacts..."
ls -lh vatican/proof/omni_ncf.tla p2p_gossip.py

echo "--------------------------------------------------"
echo "[SUCCESS] Omni-NCF fabric components bootstrapped successfully!"
