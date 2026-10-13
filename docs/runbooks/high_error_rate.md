# Incident Response & Runbook: High Error Rate

## Overview
This runbook outlines the steps to diagnose and remediate high 5xx error rates in the Enterprise AIOps Orchestrator.

## Triage Steps
1. **Check Health Probes:**
   - Verify `/health/live` and `/health/ready` endpoints.
2. **Inspect Container Logs:**
   - Run `docker logs -f <container_id>` to check for unhandled exceptions.
3. **Verify Metrics:**
   - Access Prometheus metrics at `/metrics` to identify spiking endpoints or latency bottlenecks.
