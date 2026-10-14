def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_version(client):
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json()["version"] == "1.0.0"


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "aiops_platform"
    assert len(body["merkle_root"]) == 64
    assert body["patches"] >= 1
