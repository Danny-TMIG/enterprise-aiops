from app.reality import probe_reality


def test_reality_probe():
    res = probe_reality()
    assert res["status"] == "coherent"
