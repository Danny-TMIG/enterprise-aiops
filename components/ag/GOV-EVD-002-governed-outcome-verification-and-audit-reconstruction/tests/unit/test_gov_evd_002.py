from src.public.service import GovEvd002Service


def test_gov_evd_002_service():
    svc = GovEvd002Service()
    assert svc.component_id == "GOV-EVD-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
