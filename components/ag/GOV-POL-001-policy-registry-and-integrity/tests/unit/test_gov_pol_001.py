from src.public.service import GovPol001Service


def test_gov_pol_001_service():
    svc = GovPol001Service()
    assert svc.component_id == "GOV-POL-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
