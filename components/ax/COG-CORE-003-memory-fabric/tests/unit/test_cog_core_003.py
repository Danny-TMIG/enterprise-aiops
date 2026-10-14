from src.public.service import CogCore003Service


def test_cog_core_003_service():
    svc = CogCore003Service()
    assert svc.component_id == "COG-CORE-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
