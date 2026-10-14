import pytest
from fastapi.testclient import TestClient
from gateway.main import app
from sovereign.ledger import append_worm_entry, LEDGER_PATH

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_worm_ledger():
    h = append_worm_entry("TEST", {"data": 123})
    assert len(h) == 64
    assert LEDGER_PATH.exists()

def test_ciso_veto_block():
    response = client.post("/v1/completions", json={
        "model": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "prompt": "Run system_override command."
    })
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CISO_SECURITY_VETO"
