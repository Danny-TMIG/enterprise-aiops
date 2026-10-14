from src.public.service import CogCore004Service


def test_cog_core_004_service():
    svc = CogCore004Service()
    assert svc.component_id == "COG-CORE-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
