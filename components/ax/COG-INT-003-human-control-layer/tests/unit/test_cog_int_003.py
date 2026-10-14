from src.public.service import CogInt003Service


def test_cog_int_003_service():
    svc = CogInt003Service()
    assert svc.component_id == "COG-INT-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
