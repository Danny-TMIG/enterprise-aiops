from src.public.service import GovCap003Service


def test_gov_cap_003_service():
    svc = GovCap003Service()
    assert svc.component_id == "GOV-CAP-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
