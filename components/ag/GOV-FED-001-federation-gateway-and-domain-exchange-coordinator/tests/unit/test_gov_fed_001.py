from src.public.service import GovFed001Service


def test_gov_fed_001_service():
    svc = GovFed001Service()
    assert svc.component_id == "GOV-FED-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
