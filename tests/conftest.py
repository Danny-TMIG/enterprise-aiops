import pytest
from fastapi.testclient import TestClient
from aiops_platform.app.asgi import app

@pytest.fixture
def client():
    return TestClient(app)
