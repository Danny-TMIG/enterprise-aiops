from src.public.service import CogAssur004Service


def test_cog_assur_004_service():
    svc = CogAssur004Service()
    assert svc.component_id == "COG-ASSUR-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
