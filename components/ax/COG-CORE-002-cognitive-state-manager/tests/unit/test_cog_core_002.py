from src.public.service import CogCore002Service


def test_cog_core_002_service():
    svc = CogCore002Service()
    assert svc.component_id == "COG-CORE-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
