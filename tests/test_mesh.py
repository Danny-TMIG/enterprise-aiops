from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.mesh import MeshGraph, Node, route

client = TestClient(app)

def test_mesh_graph_operations() -> None:
    graph = MeshGraph()
    node = Node(id="endpoint:/test:app/main.py:1", kind="endpoint", name="test_endpoint", file="app/main.py", line=1, extra=["api"])
    graph.add(node)
    assert "endpoint:/test:app/main.py:1" in graph.nodes
    stats = graph.stats()
    assert stats["nodes"] == 1
    assert stats["kinds"]["endpoint"] == 1

def test_mesh_router_scoring() -> None:
    graph = MeshGraph()
    graph.add(Node(id="endpoint:/mesh/route:app/main.py:10", kind="endpoint", name="mesh_route_flex", file="app/main.py", line=10))
    graph.add(Node(id="agent:omega:app/agency/omega.py:5", kind="agent", name="OmegaAgent", file="app/agency/omega.py", line=5))
    matches = route("mesh route", graph)
    assert len(matches) > 0
    assert matches[0]["name"] == "mesh_route_flex"
    assert matches[0]["score"] > 0

def test_mesh_fastapi_endpoints() -> None:
    response = client.get("/mesh/status")
    assert response.status_code == 200
    data = response.json()
    assert "root" in data
    assert "stats" in data

    response = client.post("/mesh/route", json={"intent": "cluster dispatch", "limit": 5})
    assert response.status_code == 200
    assert response.json()["status"] == "routed"

    response = client.post("/mesh/rebuild", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "rebuilt"
