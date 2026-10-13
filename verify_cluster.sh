#!/bin/bash
LOG_DIR="./logs/verification"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/health_check_$(date +%Y%m%d_%H%M%S).log"

echo "=== MLX-Omni Cluster Health Check: $(date) ===" | tee -a "$LOG_FILE"

echo "[1/3] Checking Node & Mesh Status..." | tee -a "$LOG_FILE"
python3 -m mesh.cli status --cluster mlx-omni 2>&1 | tee -a "$LOG_FILE"

echo -e "\n[2/3] Querying Local Endpoint (/health)..." | tee -a "$LOG_FILE"
curl -s http://127.0.0.1:8000/health | jq . 2>&1 | tee -a "$LOG_FILE"

echo -e "\n[3/3] Auditing Unified Memory Pressure..." | tee -a "$LOG_FILE"
sudo powermetrics -i 1000 -n 1 -s cpu_power,gpu_power 2>&1 | tee -a "$LOG_FILE"

echo -e "\n=== Verification Complete. Log saved to $LOG_FILE ==="
