import pytest
from fastapi.testclient import TestClient
from app.asgi import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_health_probes():
    live_resp = client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "alive"

    ready_resp = client.get("/health/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"
