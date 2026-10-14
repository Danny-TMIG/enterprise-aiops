from src.public.service import CogCore001Service


def test_cog_core_001_service():
    svc = CogCore001Service()
    assert svc.component_id == "COG-CORE-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
