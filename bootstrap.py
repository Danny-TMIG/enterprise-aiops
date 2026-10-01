import os
from pathlib import Path

os.makedirs("tests", exist_ok=True)
os.makedirs("scripts", exist_ok=True)

# 1. Write tests/test_mesh.py
Path("tests/test_mesh.py").write_text("""from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.mesh import MeshGraph, Node, route, get_mesh

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
""")
print("-> Created tests/test_mesh.py")

# 2. Write scripts/validate_system.py
Path("scripts/validate_system.py").write_text("""#!/usr/bin/env python3
from __future__ import annotations
import sys
import subprocess
from pathlib import Path

def main() -> None:
    print("=== [Enterprise AIOps] Automated System Validation ===")
    repo_root = Path(__file__).resolve().parent.parent
    
    print("\\n[1/3] Verifying core Python imports...")
    try:
        import fastapi
        import uvicorn
        from app.mesh import get_mesh
        print("  -> Core packages & mesh module verified successfully.")
    except Exception as e:
        print(f"  -> Import failed: {e}")
        sys.exit(1)

    print("\\n[2/3] Initializing Mesh Runtime...")
    try:
        mesh = get_mesh()
        stats = mesh.graph.stats()
        print(f"  -> Mesh graph loaded successfully: {stats['nodes']} nodes, {stats['edges']} edges across {len(stats['kinds'])} node kinds.")
    except Exception as e:
        print(f"  -> Mesh initialization failed: {e}")
        sys.exit(1)

    print("\\n[3/3] Executing test suite via pytest...")
    result = subprocess.run(["pytest", "-v"], cwd=str(repo_root))
    if result.returncode != 0:
        print("  -> Test suite reported failures.")
        sys.exit(result.returncode)
    
    print("\\n=== All validation and automation checks PASSED successfully! ===")

if __name__ == "__main__":
    main()
""")
os.chmod("scripts/validate_system.py", 0o755)
print("-> Created scripts/validate_system.py")

# 3. Update app/main.py
main_py = Path("app/main.py")
content = main_py.read_text()
if "from app.mesh import get_mesh, route" not in content:
    import_line = "from app.mesh import get_mesh, route\n"
    content = content.replace('@app.post("/mesh/route")\nasync def mesh_route_flex(payload: dict = Body(default={})):', '')
    content = content.replace('return {"status": "routed", "path": "node-0 -> node-1", "received": payload}', '')
    content = content.replace('@app.post("/mesh/rebuild")\nasync def mesh_rebuild_flex(payload: dict = Body(default={})):', '')
    content = content.replace('return {"status": "rebuilt", "active_planes": 3, "received": payload}', '')

    endpoints = """
@app.post("/mesh/route")
async def mesh_route_endpoint(payload: dict = Body(default={})):
    intent = payload.get("intent", payload.get("query", ""))
    limit = int(payload.get("limit", 20))
    mesh = get_mesh()
    matches = route(intent, mesh.graph, limit=limit)
    return {"status": "routed", "intent": intent, "matches": matches, "mesh_stats": mesh.graph.stats()}

@app.post("/mesh/rebuild")
async def mesh_rebuild_endpoint(payload: dict = Body(default={})):
    mesh = get_mesh()
    stats = mesh.rebuild()
    return {"status": "rebuilt", "runtime_status": mesh.status(), "stats": stats}

@app.get("/mesh/status")
async def mesh_status_endpoint():
    mesh = get_mesh()
    return mesh.status()
"""
    main_py.write_text(import_line + content.strip() + "\n" + endpoints)
    print("-> Updated app/main.py with live mesh endpoints.")

print("\\nInitialization script written successfully.")
