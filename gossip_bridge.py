import asyncio
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GossipBridge")

class ClusterGossipClient:
    def __init__(self, primary_port: int = 9001):
        self.primary_port = primary_port

    async def get_cluster_state(self) -> Dict[str, Any]:
        """Queries the local P2P gossip node for active cluster telemetry and epoch."""
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", self.primary_port)
            
            # Send gateway query packet first to unblock server's read()
            query_payload = json.dumps({"status": "gateway_query", "epoch": 9999}).encode("utf-8")
            writer.write(query_payload)
            await writer.drain()
            
            # Now read the server's response state
            data = await reader.read(4096)
            writer.close()
            await writer.wait_closed()
            
            if data:
                state = json.loads(data.decode("utf-8"))
                logger.info(f"Successfully retrieved cluster state from port {self.primary_port}")
                return state
        except Exception as e:
            logger.warning(f"Could not reach gossip node on port {self.primary_port}: {e}")
        
        return {
            "status": "degraded",
            "model": "mlx-community/Qwen2.5-7B-Instruct-4bit",
            "epoch": -1,
            "error": "Gossip node unreachable"
        }

# Singleton instance for FastAPI integration
bridge = ClusterGossipClient()

if __name__ == "__main__":
    state = asyncio.run(bridge.get_cluster_state())
    print(json.dumps(state, indent=2))
