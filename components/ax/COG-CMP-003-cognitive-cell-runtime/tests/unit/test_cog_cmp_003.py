from src.public.service import CogCmp003Service


def test_cog_cmp_003_service():
    svc = CogCmp003Service()
    assert svc.component_id == "COG-CMP-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
