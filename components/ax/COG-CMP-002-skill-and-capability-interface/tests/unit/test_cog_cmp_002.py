from src.public.service import CogCmp002Service


def test_cog_cmp_002_service():
    svc = CogCmp002Service()
    assert svc.component_id == "COG-CMP-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
