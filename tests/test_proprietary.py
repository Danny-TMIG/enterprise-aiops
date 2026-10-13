from app.core.registry import ProprietaryRegistry


def test_proprietary_registry_interface():
    reg = ProprietaryRegistry()
    assert reg.reality_score() == 1.0
    st = reg.status()
    assert "registered_objects" in st
    res = reg.invoke("microsoft", {"action": "ping"})
    assert res["execution"] == "success"
