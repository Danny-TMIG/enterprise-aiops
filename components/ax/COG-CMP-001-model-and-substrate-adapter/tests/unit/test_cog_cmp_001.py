from src.public.service import CogCmp001Service


def test_cog_cmp_001_service():
    svc = CogCmp001Service()
    assert svc.component_id == "COG-CMP-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
