from src.public.service import GovInf003Service


def test_gov_inf_003_service():
    svc = GovInf003Service()
    assert svc.component_id == "GOV-INF-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
