from src.public.service import CogInt002Service


def test_cog_int_002_service():
    svc = CogInt002Service()
    assert svc.component_id == "COG-INT-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
