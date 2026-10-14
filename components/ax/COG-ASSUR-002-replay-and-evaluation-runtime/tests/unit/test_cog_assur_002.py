from src.public.service import CogAssur002Service


def test_cog_assur_002_service():
    svc = CogAssur002Service()
    assert svc.component_id == "COG-ASSUR-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
